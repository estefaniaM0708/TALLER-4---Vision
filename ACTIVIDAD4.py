import cv2
import mediapipe as mp
import time
import serial   # Nueva importación

# Inicializar puerto serie (Reemplaza 'COM5' por el puerto de tu ESP32)
try:
    esp32 = serial.Serial('COM8', 115200, timeout=1)
    print("Conectado al COM8. Esperando inicio del ESP32...")
    time.sleep(2)     # <--- CLAVE: Dale 2 segundos al ESP32 para arrancar
except Exception as e:
    print(f"Error al abrir el puerto: {e}")
    esp32 = None

# Clases principales de la API de MediaPipe Tasks
BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Gestos de interés
TARGET_GESTURES = ["Closed_Fist", "Victory", "Open_Palm", "Thumb_Up", "Thumb_Down"]

# Mapeo de gesto de MediaPipe -> comando para el ESP32
GESTURE_TO_COMMAND = {
    "Closed_Fist": 'F',     # 30% brillo
    "Victory": 'V',         # 70% brillo
    "Open_Palm": 'P',       # 100% brillo
    "Thumb_Up": 'U',        # Secuencia 1
    "Thumb_Down": 'D',      # Secuencia 2
}

# Configuración del reconocedor en modo VIDEO
options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path="gesture_recognizer.task"),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1
)

last_command_sent = None    # Para no reenviar el mismo comando en cada frame

with GestureRecognizer.create_from_options(options) as recognizer:
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convertir de BGR (OpenCV) a RGB y luego a mp.Image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # MediaPipe exige un timestamp en milisegundos para secuencias de video
        timestamp_ms = int(time.time() * 1000)

        # Procesar el fotograma
        result = recognizer.recognize_for_video(mp_image, timestamp_ms)

        # Filtrar y dibujar resultados
        if result.gestures:
            top_gesture = result.gestures[0][0]
            gesture_name = top_gesture.category_name
            score = top_gesture.score
            if gesture_name in TARGET_GESTURES:
                cv2.putText(
                    frame,
                    f"Gesto: {gesture_name} ({score:.1%})",
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

                # Enviar comando al ESP32 solo si cambió el gesto
                command = GESTURE_TO_COMMAND.get(gesture_name)
                if command and command != last_command_sent and esp32 is not None:
                    esp32.write(command.encode('utf-8'))
                    last_command_sent = command
                    print(f"Enviado: {command}")

        cv2.imshow("MediaPipe Gesture Recognizer", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    if esp32 is not None:
        esp32.close()