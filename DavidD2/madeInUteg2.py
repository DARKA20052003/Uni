import os
import glob
import cv2
import mediapipe as mp
import serial
import time
import pywhatkit as kit
import signal
import subprocess

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

### --- CERRAR OTRA INSTANCIA PREVIA --- ###
proc_name = "made_In_Uteg.py"
result = subprocess.run(["pgrep", "-f", proc_name], capture_output=True, text=True)
for pid in result.stdout.split():
    if pid and int(pid) != os.getpid():
        print(f"[INFO] Cerrando instancia previa PID {pid}")
        os.kill(int(pid), signal.SIGTERM)

### --- CONFIGURACIÓN --- ###
numeros_emergencia = [
    "+593962600990",
]

mensaje_auxilio = "🚨 ¡Emergencia! Se ha confirmado una alerta con gestos. Por favor, contactar con la persona inmediatamente."

def enviar_mensajes_emergencia():
    for numero in numeros_emergencia:
        print(f"[WhatsApp] Enviando mensaje a {numero}...")
        try:
            kit.sendwhatmsg_instantly(numero, mensaje_auxilio, wait_time=10, tab_close=True)
            time.sleep(15)
        except Exception as e:
            print(f"[Error WhatsApp] {e}")

### --- DETECCIÓN AUTOMÁTICA DEL ARDUINO --- ###
def detectar_puerto_arduino():
    posibles_puertos = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    return posibles_puertos[0] if posibles_puertos else None

puerto_arduino = detectar_puerto_arduino()
arduino = None
if puerto_arduino:
    try:
        arduino = serial.Serial(puerto_arduino, 9600, timeout=1)
        time.sleep(2)
        print(f"[Arduino] Conectado en {puerto_arduino}")
    except Exception as e:
        print(f"[Error Arduino] No se pudo abrir {puerto_arduino}: {e}")
else:
    print("[Advertencia] No se encontró Arduino conectado.")

### --- CONFIGURACIÓN MEDIAPIPE --- ###
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.85,
    min_tracking_confidence=0.85
)
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

class State:
    WAITING_ALERT = 0
    WAITING_CONFIRM = 1
    COMPLETE = 2

current_state = State.WAITING_ALERT

def get_finger_states(landmarks, is_right_hand):
    states = []
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    vec_thumb = (thumb_tip.x - thumb_ip.x, thumb_tip.y - thumb_ip.y)
    vec_index = (landmarks[5].x - landmarks[0].x, landmarks[5].y - landmarks[0].y)
    cross = vec_thumb[0] * vec_index[1] - vec_thumb[1] * vec_index[0]
    thumb_extended = cross > 0 if is_right_hand else cross < 0
    states.append(1 if thumb_extended else 0)

    finger_pairs = [(8,6), (12,10), (16,14), (20,18)]
    margins = [0.03, 0.03, 0.05, 0.03]
    for (tip, pip), margin in zip(finger_pairs, margins):
        states.append(1 if landmarks[tip].y < landmarks[pip].y - margin else 0)
    return states

### --- INICIALIZACIÓN DE CÁMARA --- ###
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

if not cap.isOpened():
    print("[Error Cámara] No se pudo acceder a la cámara.")
    exit()

# Crear ventana una sola vez
cv2.namedWindow('Detección de Gestos', cv2.WINDOW_NORMAL)

ultima_alerta = 0
tiempo_bloqueo = 30  # segundos de espera antes de permitir otra alerta

try:
    while True:
        success, image = cap.read()
        if not success:
            print("[Advertencia] No se pudo leer un frame de la cámara.")
            break

        image = cv2.flip(image, 1)
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        alert_active = False
        confirm_active = False
        cancel_active = False
        right_ok = False
        left_ok = False

        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                is_right = handedness.classification[0].label == "Right"
                finger_states = get_finger_states(hand_landmarks.landmark, is_right)

                hand_color = (0, 255, 0) if is_right else (0, 0, 255)
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

                hand_type = "Derecha" if is_right else "Izquierda"
                y_pos = 50 if is_right else 80
                cv2.putText(image, f"{hand_type}: {finger_states}",
                            (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, hand_color, 1)

                if is_right:
                    alert_active = all(finger_states)
                    right_ok = (finger_states == [1, 0, 0, 0, 0])
                else:
                    confirm_active = (finger_states == [1, 1, 1, 0, 1])
                    left_ok = (finger_states == [1, 0, 0, 0, 0])

            cancel_active = right_ok and left_ok

        state_text = ["Esperando Alerta", "Esperando Confirmación", "Secuencia Completa"][current_state]
        cv2.putText(image, f"Estado: {state_text}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Transiciones de estado
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
                print(">>> Enviando mensajes de auxilio por WhatsApp <<<")
                enviar_mensajes_emergencia()
                ultima_alerta = ahora
                time.sleep(5)
            else:
                print(">>> Alerta ignorada: en tiempo de bloqueo <<<")
            current_state = State.WAITING_ALERT

        elif current_state != State.WAITING_ALERT and cancel_active:
            current_state = State.WAITING_ALERT
            if arduino:
                arduino.write(b'0')  # Apagar LED
            print(">>> GESTO DE CANCELACIÓN DETECTADO <<<")
            print(">>> Alarma cancelada <<<")
            time.sleep(2)

        cv2.imshow('Detección de Gestos', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

except KeyboardInterrupt:
    print("\n[INFO] Programa detenido manualmente.")
except Exception as e:
    print(f"[Error] {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()
    if arduino:
        arduino.close()
