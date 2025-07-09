import cv2

cap = cv2.VideoCapture(0)  # Cambia el número si tienes varias cámaras

if not cap.isOpened():
    print("No se pudo abrir la cámara.")
    exit

cv2.namedWindow("Prueba de cámara", cv2.WINDOW_NORMAL)
print ("Presiona 'q' para salir.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: no se puede leer la cámara.")
        break

    cv2.imshow("Prueba de cámara", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()