import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Cambia el número si tienes varias cámaras

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: no se puede leer la cámara.")
        break

    cv2.imshow("Prueba de cámara", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()