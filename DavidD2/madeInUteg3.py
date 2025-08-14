import os
import cv2
import glob
import serial
import time
import subprocess
import signal
import webbrowser
from urllib.parse import quote
import shutil

# --- Ajustes OpenCV / logs ---
cv2.setUseOptimized(True)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # silencia logs de TF si alguna lib lo usa

# --- Cerrar otra instancia previa (evita ventanas duplicadas) ---
PROC_NAME = "made_In_Uteg.py"
try:
    out = subprocess.run(["pgrep", "-f", PROC_NAME], capture_output=True, text=True).stdout.split()
    for pid in out:
        if pid and int(pid) != os.getpid():
            print(f"[INFO] Cerrando instancia previa PID {pid}")
            os.kill(int(pid), signal.SIGTERM)
except Exception:
    pass

# --- Configuración de emergencia ---
numeros_emergencia = ["+593979216140"]
mensaje_auxilio = "🚨 ¡Emergencia! Se ha confirmado una alerta con gestos. Por favor, contactar con la persona inmediatamente."

def abrir_whatsapp_web(numero: str, mensaje: str):
    """
    Abre WhatsApp Web con el chat y el texto prellenado.
    Compatible con Brave (snap), otros navegadores y xdg-open.
    """
    url = f"https://web.whatsapp.com/send?phone={numero}&text={quote(mensaje)}"

    # 1) Si existe comando 'brave' / 'brave-browser' (snap o deb), úsalo explícitamente
    brave_cmd = shutil.which("brave") or shutil.which("brave-browser")
    if brave_cmd:
        try:
            subprocess.Popen([brave_cmd, "--new-tab", url],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except Exception as e:
            print(f"[Aviso] Lanzar Brave falló: {e}")

    # 2) Intentar con el navegador por defecto de Python
    try:
        webbrowser.open(url, new=2)  # nueva pestaña si es posible
        return
    except Exception as e:
        print(f"[Aviso] webbrowser.open falló: {e}")

    # 3) Último recurso: xdg-open
    try:
        subprocess.Popen(["xdg-open", url],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[Error] No se pudo abrir el navegador: {e}")

def enviar_mensajes_emergencia():
    for numero in numeros_emergencia:
        print(f"[WhatsApp] Abriendo chat con {numero} (envío manual)…")
        abrir_whatsapp_web(numero, mensaje_auxilio)
        print("   ➜ En la pestaña, presiona Enter para enviar.")
        time.sleep(2)  # pequeña pausa entre contactos

# --- Detectar puerto Arduino en Linux ---
def detectar_puerto_arduino():
    puertos = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    return puertos[0] if puertos else None

arduino = None
puerto = detectar_puerto_arduino()
if puerto:
    try:
        arduino = serial.Serial(puerto, 9600, timeout=1)
        time.sleep(2)
        print(f"[Arduino] Conectado en {puerto}")
    except Exception as e:
        print(f"[Error Arduino] {e}")
else:
    print("[Advertencia] No se encontró Arduino conectado.")

# --- MediaPipe Hands (config ligera y rápida) ---
import mediapipe as mp
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    model_complexity=0,              # más ligero
    min_detection_confidence=0.55,
    min_tracking_confidence=0.55
)
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

# --- Cámara con V4L2 + MJPEG para menos CPU ---
def abrir_camara():
    # Forzar backend V4L2 si está disponible
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)  # fallback
    # Pedir MJPG (si la webcam lo soporta, reduce CPU)
    try:
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        cap.set(cv2.CAP_PROP_FOURCC, fourcc)
    except Exception:
        pass
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # calidad visual fluida
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)            # objetivo de fluidez
    # Evita buffering largo (si el backend lo soporta)
    try:
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except Exception:
        pass
    return cap

cap = abrir_camara()
if not cap.isOpened():
    print("[Error Cámara] No se pudo acceder a la cámara.")
    raise SystemExit(1)

# Ventana única
cv2.namedWindow('Detección de Gestos', cv2.WINDOW_NORMAL)

# --- Estados ---
class State:
    WAITING_ALERT = 0
    WAITING_CONFIRM = 1
    COMPLETE = 2

current_state = State.WAITING_ALERT
ultima_alerta = 0
tiempo_bloqueo = 30  # segundos

# --- Utilidades de gesto ---
def get_finger_states(landmarks, is_right_hand):
    # landmarks: normalizados [0..1]
    states = []
    thumb_tip = landmarks[4]; thumb_ip = landmarks[3]
    vec_thumb = (thumb_tip.x - thumb_ip.x, thumb_tip.y - thumb_ip.y)
    vec_index = (landmarks[5].x - landmarks[0].x, landmarks[5].y - landmarks[0].y)
    cross = vec_thumb[0] * vec_index[1] - vec_thumb[1] * vec_index[0]
    thumb_extended = cross > 0 if is_right_hand else cross < 0
    states.append(1 if thumb_extended else 0)
    finger_pairs = [(8,6), (12,10), (16,14), (20,18)]
    margins = [0.03, 0.03, 0.05, 0.03]
    for (tip, pip), m in zip(finger_pairs, margins):
        states.append(1 if landmarks[tip].y < landmarks[pip].y - m else 0)
    return states

# --- Bucle principal (procesa cada frame, MediaPipe en downscale) ---
target_proc_width = 224  # ancho para procesar gestos (rápido)
flip_view = True

try:
    while True:
        ok, frame = cap.read()
        if not ok:
            print("[Advertencia] No se pudo leer un frame de la cámara.")
            break

        # Vista fluida en 640x480; procesamos copia reducida
        display = cv2.flip(frame, 1) if flip_view else frame
        h, w = display.shape[:2]
        scale = target_proc_width / float(w)
        proc_img = cv2.resize(display, (target_proc_width, int(h * scale)), interpolation=cv2.INTER_AREA)

        # MediaPipe requiere RGB
        proc_rgb = cv2.cvtColor(proc_img, cv2.COLOR_BGR2RGB)
        results = hands.process(proc_rgb)

        alert_active = confirm_active = False
        right_ok = left_ok = False

        if results and results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                is_right = handedness.classification[0].label == "Right"
                finger_states = get_finger_states(hand_landmarks.landmark, is_right)

                # Dibujar (sobre la imagen display de 640x480)
                mp_drawing.draw_landmarks(
                    display,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style()
                )

                if is_right:
                    alert_active = all(finger_states)
                    right_ok = (finger_states == [1, 0, 0, 0, 0])
                else:
                    confirm_active = (finger_states == [1, 1, 1, 0, 1])
                    left_ok = (finger_states == [1, 0, 0, 0, 0])

            cancel_active = right_ok and left_ok
        else:
            cancel_active = False

        # Estado en pantalla
        state_text = ["Esperando Alerta", "Esperando Confirmación", "Secuencia Completa"][current_state]
        cv2.putText(display, f"Estado: {state_text}", (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Transiciones
        if current_state == State.WAITING_ALERT and alert_active:
            current_state = State.WAITING_CONFIRM
            print(">>> ALERTA DETECTADA <<<")

        elif current_state == State.WAITING_CONFIRM and confirm_active:
            ahora = time.time()
            if ahora - ultima_alerta > tiempo_bloqueo:
                current_state = State.COMPLETE
                if arduino:
                    arduino.write(b'1')
                print(">>> CONFIRMACIÓN DETECTADA - LED ENCENDIDO <<<")
                print(">>> Abriendo WhatsApp Web (envío manual) <<<")
                enviar_mensajes_emergencia()
                ultima_alerta = ahora
                time.sleep(2)  # pequeña pausa tras abrir chats
            else:
                print(">>> Alerta ignorada: en tiempo de bloqueo <<<")
            current_state = State.WAITING_ALERT

        elif current_state != State.WAITING_ALERT and cancel_active:
            current_state = State.WAITING_ALERT
            if arduino:
                arduino.write(b'0')
            print(">>> GESTO DE CANCELACIÓN DETECTADO <<<")
            print(">>> Alarma cancelada <<<")
            time.sleep(0.3)

        # Mostrar
        cv2.imshow('Detección de Gestos', display)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

except KeyboardInterrupt:
    print("\n[INFO] Programa detenido manualmente.")
finally:
    cap.release()
    cv2.destroyAllWindows()
    if arduino:
        arduino.close()
