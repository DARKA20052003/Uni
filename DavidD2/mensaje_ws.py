import pywhatkit as kit
import time

# Lista de números (con '+' y código de país)
numeros = [
    "+5930962600990",
    "+5930959723043"
]

# Mensaje a enviar
mensaje = "¡Hola! Este mensaje fue enviado automáticamente con Python 📲"

# Espera entre mensajes (segundos)
espera_entre_mensajes = 15

# Enviar mensajes uno por uno
for numero in numeros:
    print(f"Enviando mensaje a {numero}...")
    kit.sendwhatmsg_instantly(numero, mensaje, wait_time=10, tab_close=True)
    time.sleep(espera_entre_mensajes)
