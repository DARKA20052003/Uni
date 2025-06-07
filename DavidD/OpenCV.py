import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
import mediapipe as mp
import serial
import time
import math

# Configuración inicial
arduino = serial.Serial('COM9', 9600, timeout=1)
time.sleep(2)

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
    
    # Detección del pulgar (mejorada)
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    vec_thumb = (thumb_tip.x - thumb_ip.x, thumb_tip.y - thumb_ip.y)
    vec_index = (landmarks[5].x - landmarks[0].x, landmarks[5].y - landmarks[0].y)
    cross = vec_thumb[0] * vec_index[1] - vec_thumb[1] * vec_index[0]
    thumb_extended = cross > 0 if is_right_hand else cross < 0
    states.append(1 if thumb_extended else 0)
    
    # Otros dedos (con márgenes)
    finger_pairs = [(8,6), (12,10), (16,14), (20,18)]
    margins = [0.03, 0.03, 0.05, 0.03]
    for (tip, pip), margin in zip(finger_pairs, margins):
        states.append(1 if landmarks[tip].y < landmarks[pip].y - margin else 0)
    return states

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 250)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 150)

try:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        # Procesamiento de imagen
        image = cv2.flip(image, 1)  # Flip horizontal primero
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        # Dibujo y detección
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        alert_active = False
        confirm_active = False
        
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, 
                                                results.multi_handedness):
                is_right = handedness.classification[0].label == "Right"
                finger_states = get_finger_states(hand_landmarks.landmark, is_right)
                
                # Dibujar landmarks
                hand_color = (0, 255, 0) if is_right else (0, 0, 255)
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
                
                # Mostrar estados
                hand_type = "Derecha" if is_right else "Izquierda"
                y_pos = 50 if is_right else 80
                cv2.putText(image, f"{hand_type}: {finger_states}", 
                           (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, hand_color, 1)
                
                # Detección de gestos
                if is_right:
                    alert_active = all(finger_states)
                else:
                    confirm_active = (finger_states == [1, 1, 1, 0, 1])  # Corregido a [1,1,1,0,1]

        # Máquina de estados
        state_text = ["Esperando Alerta", "Esperando Confirmación", "Secuencia Completa"][current_state]
        cv2.putText(image, f"Estado: {state_text}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        if current_state == State.WAITING_ALERT and alert_active:
            current_state = State.WAITING_CONFIRM
            print(">>> ALERTA DETECTADA <<<")
        elif current_state == State.WAITING_CONFIRM and confirm_active:
            current_state = State.COMPLETE
            arduino.write(b'1')
            print(">>> CONFIRMACIÓN DETECTADA - LED ENCENDIDO <<<")
            time.sleep(2)
            current_state = State.WAITING_ALERT

        cv2.imshow('Detección de Gestos', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

except Exception as e:
    print(f"Error: {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()
    arduino.close()