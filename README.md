# Actividad 4 — Reconocimiento de gestos mediante MediaPipe y comunicación con ESP32

## Descripción del proyecto

En esta actividad se desarrolló un sistema de reconocimiento de gestos de la mano utilizando visión artificial mediante **MediaPipe Gesture Recognizer** y procesamiento de imágenes con **OpenCV**.

El sistema utiliza la cámara del computador para capturar imágenes en tiempo real, identificar diferentes gestos realizados con la mano y enviar comandos mediante comunicación serial hacia una ESP32.

La ESP32 recibe los comandos generados por el reconocimiento visual y puede utilizarlos para controlar diferentes acciones dentro de un sistema embebido.

El proyecto integra:

- Captura de video mediante OpenCV.
- Reconocimiento de gestos con MediaPipe.
- Modelo de inteligencia artificial para clasificación de gestos.
- Comunicación serial UART entre computador y ESP32.
- Procesamiento en tiempo real.

---

# Arquitectura del sistema

```text
              Cámara
                 |
                 |
                 v
            OpenCV
                 |
                 |
                 v
        MediaPipe Gesture
          Recognizer
                 |
                 |
                 v
        Clasificación gesto
                 |
                 |
                 v
          Comunicación Serial
                 |
                 |
                 v
              ESP32
                 |
                 |
                 v
        Acción del sistema embebido
```

---

# Hardware utilizado

## ESP32

La ESP32 funciona como dispositivo receptor de comandos enviados desde el computador mediante comunicación serial.

Funciones:

- Recibir comandos enviados por USB.
- Ejecutar acciones asociadas a los gestos detectados.

---

# Software utilizado

## Computador

Lenguaje:

```text
Python
```

Librerías utilizadas:

```text
opencv-python
mediapipe
pyserial
time
```

---

# Organización del proyecto

```text
Actividad_4/

│
├── ACTIVIDAD4.py
│
├── gesture_recognizer.task
│
├── README.md
│
└── ESP32/
    |
    └── main.py
```

---

# Funcionamiento del sistema

## 1. Captura de imagen

El sistema inicia la cámara utilizando OpenCV:

```python
cv2.VideoCapture(0)
```

Cada fotograma capturado es procesado para identificar la posición de la mano.

---

# 2. Procesamiento con MediaPipe

La imagen obtenida por la cámara se convierte al formato requerido por MediaPipe:

```python
cv2.cvtColor()
```

Posteriormente se genera una imagen compatible con el reconocedor:

```python
mp.Image()
```

El modelo utilizado corresponde al archivo:

```text
gesture_recognizer.task
```

El reconocimiento funciona en modo VIDEO utilizando:

```python
VisionRunningMode.VIDEO
```

---

# 3. Gestos reconocidos

El sistema identifica los siguientes gestos:

| Gesto | Comando enviado |
|---|---|
| Closed_Fist | F |
| Victory | V |
| Open_Palm | P |
| Thumb_Up | U |
| Thumb_Down | D |

La relación entre gesto y comando se realiza mediante un diccionario de asignación:

```python
GESTURE_TO_COMMAND
```

---

# 4. Comunicación serial con ESP32

La comunicación entre el computador y la ESP32 se realiza mediante puerto serial.

Configuración:

```text
Baudrate:
115200
```

Ejemplo:

```python
serial.Serial('COM5',115200)
```

Cuando un gesto es detectado, el sistema envía un carácter correspondiente:

Ejemplo:

```text
Gesto:
Victory

Comando enviado:
V
```

---

# 5. Filtrado de comandos

Para evitar enviar el mismo comando continuamente en cada fotograma, el programa almacena el último comando enviado:

```python
last_command_sent
```

El comando solo se transmite cuando existe un cambio de gesto detectado.

---

# Gestos utilizados

## Closed_Fist

Representa:

```text
F
```

Acción asociada:

```text
Control 30%
```

---

## Victory

Representa:

```text
V
```

Acción asociada:

```text
Control 70%
```

---

## Open_Palm

Representa:

```text
P
```

Acción asociada:

```text
Control 100%
```

---

## Thumb_Up

Representa:

```text
U
```

Acción asociada:

```text
Secuencia 1
```

---

## Thumb_Down

Representa:

```text
D
```

Acción asociada:

```text
Secuencia 2
```

---

# Ejecución del proyecto

## Instalación de librerías

Ejecutar:

```bash
pip install opencv-python mediapipe pyserial
```

---

## Conectar ESP32

Verificar el puerto:

```bash
python -m serial.tools.list_ports
```

Ejemplo:

```text
COM5
```

---

## Ejecutar reconocimiento

Ejecutar:

```bash
python ACTIVIDAD4.py
```

Al iniciar:

1. Se abre la cámara.
2. MediaPipe analiza la imagen.
3. Se muestra el gesto detectado.
4. Se envía el comando correspondiente a la ESP32.

---

# Evidencia de funcionamiento

El sistema permite observar:

- Captura de video en tiempo real.
- Identificación del gesto realizado.
- Visualización del nombre del gesto detectado.
- Envío del comando hacia la ESP32.

Ejemplo:

```text
Gesto detectado:
Open_Palm

Comando enviado:
P
```

---

# Comunicación utilizada

| Tecnología | Función |
|---|---|
| Cámara | Captura de imágenes |
| OpenCV | Procesamiento de video |
| MediaPipe | Reconocimiento de gestos |
| UART Serial | Comunicación PC-ESP32 |
| ESP32 | Ejecución de comandos |

---

# Resultados obtenidos

El sistema logró reconocer diferentes gestos de la mano utilizando inteligencia artificial y enviar comandos hacia un sistema embebido.

La integración entre visión artificial y comunicación serial permite desarrollar una interfaz de control sin contacto físico, utilizando únicamente movimientos realizados frente a la cámara.

---

# Conclusión

La actividad permitió implementar un sistema basado en visión artificial capaz de interpretar gestos humanos y convertirlos en comandos digitales.

MediaPipe permitió realizar la clasificación de gestos en tiempo real, mientras que OpenCV facilitó la captura y procesamiento de imágenes. Finalmente, la comunicación serial permitió integrar el reconocimiento visual con una plataforma embebida basada en ESP32.
