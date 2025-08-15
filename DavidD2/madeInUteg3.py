import os
import cv2
import glob
import serial
import time
import subprocess
import signal
import webbrowser
from urllib.parse import urlencode, quote
import re

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

# --- Forzar Brave (.deb) como navegador para PyWhatKit/webbrowser ---
def configurar_brave_default():
    # Rutas típicas de Brave .deb
    posibles = ["/usr/bin/brave-browser", "/usr/bin/brave"]
    brave_path = next((p for p in posibles if os.path.exists(p)), None)
    if brave_path:
        try:
            webbrowser.register('brave', None, webbrowser.BackgroundBrowser(brave_path))
            webbrowser.get('brave')  # valida registro
            os.environ["BROWSER"] = "brave"
            print(f"[WhatsApp] Usando Brave en {brave_path} para abrir WhatsApp Web.")
            return True
        except Exception as e:
            print(f"[Aviso] No se pudo fijar Brave: {e}")
    else:
        print("[Aviso] No encontré Brave en /usr/bin. Se usará el navegador por defecto del sistema.")
    return False

configurar_brave_default()

# --- Envío WhatsApp: preferir PyWhatKit (automático) y fallback a abrir URL ---
import pywhatkit as kit

def _normalizar_e164(numero: str, default_cc: str = "593") -> str:
    """Convierte a E.164 con '+'. Acepta +593..., 009593..., 0xxxxxxxxx (EC), 593..."""
    d = re.sub(r'\D', '', numero or "")
    if not d:
        return ""
    if d.startswith("00"):
        d = d[2:]
    if d.startswith(default_cc):
        return "+" + d
    if d.startswith("0") and len(d) == 10:     # 0xxxxxxxxx (Ecuador)
        return "+" + default_cc + d[1:]
    if len(d) == 9 and d.startswith("9"):      # 9xxxxxxxx (celular EC)
        return "+" + default_cc + d
    if len(d) >= 10:
        return "+" + d
    return "+" + d

def _abrir_url_generico(numero_sin_mas: str, mensaje: str):
    """Abre chat para envío manual si falla PyWhatKit."""
    params = {"phone": numero_sin_mas, "text": mensaje}
    url_api = "https://api.whatsapp.com/send?" + urlencode(params, quote_via=quote)
    try:
        webbrowser.open(url_api, new=2)
    except Exception:
        try:
            subprocess.Popen(["xdg-open", url_api],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[Error] No se pudo abrir el navegador: {e}")
            print(f"➡️ Copia/pega esta URL: {url_api}")

def enviar_mensajes_emergencia():
    for numero in numeros_emergencia:
        e164 = _normalizar_e164(numero)
        if not e164 or not e164.startswith("+"):
            print(f"[Error] Número inválido: {numero}")
            continue
        print(f"[WhatsApp] Enviando mensaje a {e164}...")
        try:
            # PyWhatKit abre Brave (registrado arriba) y automatiza el 'Enter'
            kit.sendwhatmsg_instantly(e164, mensaje_auxilio, wait_time=70, tab_close=False)
            time.sleep(80)  # dejar tiempo a la automatización a completar
        except Exception as e:
            print(f"[PyWhatKit falló: {e}] → Abriendo chat para envío manual.")
            # quitar '+' para la URL api.whatsapp.com
            numero_sin_mas = e164[1:]
            _abrir_url_generico(numero_sin_mas, mensaje_auxilio)
            print("   ➜ En la pestaña, presiona Enter para enviar.")
            time.sleep(2)

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
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)  # fallback
    try:
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        cap.set(cv2.CAP_PROP_FOURCC, fourcc)
    except Exception:
        pass
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
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

        display = cv2.flip(frame, 1) if flip_view else frame
        h, w = display.shape[:2]
        scale = target_proc_width / float(w)
        proc_img = cv2.resize(display, (target_proc_width, int(h * scale)), interpolation=cv2.INTER_AREA)

        proc_rgb = cv2.cvtColor(proc_img, cv2.COLOR_BGR2RGB)
        results = hands.process(proc_rgb)

        alert_active = confirm_active = False
        right_ok = left_ok = False

        if results and results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                is_right = handedness.classification[0].label == "Right"
                finger_states = get_finger_states(hand_landmarks.landmark, is_right)

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
                print(">>> Enviando mensajes de auxilio por WhatsApp (Brave) <<<")
                enviar_mensajes_emergencia()
                ultima_alerta = ahora
                time.sleep(2)
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
