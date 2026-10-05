# Actividad 4 — Control de un LED con gestos de la mano (MediaPipe + ESP32)

## Descripción del proyecto

En esta actividad se desarrolló un sistema que reconoce **gestos de la mano** con la cámara del computador y los usa para controlar **un LED** conectado a una **ESP32**.

El computador ejecuta un programa en Python que captura video con **OpenCV**, reconoce el gesto con el modelo **Gesture Recognizer de MediaPipe** y envía una letra por **USB serie** a la ESP32. La ESP32, programada en **MicroPython**, interpreta esa letra y cambia el brillo del LED mediante **PWM** o ejecuta una secuencia de luz.

El proyecto integra:

- Visión por computador con OpenCV.
- Reconocimiento de gestos con MediaPipe Tasks.
- Comunicación serial USB entre el computador y la ESP32.
- Programación embebida con MicroPython.
- Control de brillo de un LED mediante PWM.

---

# Arquitectura del sistema

```text
        Cámara del PC
              |
              v
     Computador (Python)
  OpenCV + MediaPipe Gesture Recognizer
       (ACTIVIDAD4.py)
              |
         USB Serial
       (COM8, 115200)
              |
              v
           ESP32
       (MicroPython)
         (main.py)
              |
             PWM
              |
              v
     LED + resistencia 220 Ω
```

---

# Gestos y acciones

| Gesto | Nombre en MediaPipe | Comando enviado | Acción del LED |
|---|---|---|---|
| ✊ Puño cerrado | `Closed_Fist` | `F` | Brillo al 30 % |
| ✌️ Victoria | `Victory` | `V` | Brillo al 70 % |
| ✋ Palma abierta | `Open_Palm` | `P` | Brillo al 100 % |
| 👍 Pulgar arriba | `Thumb_Up` | `U` | Secuencia 1: "respiración" (el brillo sube y baja) |
| 👎 Pulgar abajo | `Thumb_Down` | `D` | Secuencia 2: parpadeo rápido |

---

# Hardware utilizado

- 1 × ESP32 con firmware MicroPython.
- 1 × LED.
- 1 × resistencia de 220 Ω.
- Cables Dupont y protoboard.
- 1 × cable USB de datos.
- Computador con cámara web.

## Conexión del LED

| Elemento | Conexión |
|---|---|
| GPIO 4 | Resistencia de 220 Ω |
| Resistencia | Pata larga (+, ánodo) del LED |
| Pata corta (−, cátodo) del LED | GND de la ESP32 |

```text
 ESP32
 GPIO4 ──[ 220 Ω ]──▶|── GND
                 ánodo (+)  cátodo (−)
```

La resistencia limita la corriente del LED para proteger tanto el LED como el pin de la ESP32.

---

# Organización del proyecto

```text
actividad 4/
├── ACTIVIDAD4.py            ← programa del computador (cámara + MediaPipe + envío serial)
├── gesture_recognizer.task  ← modelo de MediaPipe para reconocer gestos
├── main.py                  ← programa de la ESP32 (control del LED)
└── README.md
```

| Archivo | Dónde se ejecuta | Función |
|---|---|---|
| `ACTIVIDAD4.py` | Computador | Captura la cámara, reconoce el gesto y envía la letra por USB |
| `gesture_recognizer.task` | Computador | Modelo entrenado de MediaPipe |
| `main.py` | ESP32 | Recibe la letra y controla el LED |

---

# Funcionamiento del sistema

## 1. Captura y reconocimiento (computador)

`ACTIVIDAD4.py` abre la cámara con OpenCV. Cada fotograma se convierte de BGR a RGB y se entrega al **Gesture Recognizer** de MediaPipe en modo `VIDEO`, junto con una marca de tiempo en milisegundos.

El modelo devuelve el gesto más probable y su nivel de confianza, que se muestran sobre la imagen:

```text
Gesto: Open_Palm (92.5%)
```

## 2. Envío por puerto serie

Cada gesto se traduce a una letra con el diccionario `GESTURE_TO_COMMAND`. Solo se envía cuando el gesto **cambia**, para no saturar el puerto repitiendo el mismo comando en cada fotograma:

```python
if command and command != last_command_sent and esp32 is not None:
    esp32.write(command.encode('utf-8'))
    last_command_sent = command
```

Parámetros de la comunicación:

```text
Puerto: COM8
Velocidad: 115200 baudios
```

## 3. Control del LED (ESP32)

`main.py` lee el puerto USB **sin bloquear** el programa, con `select.poll()`. Así la ESP32 puede recibir comandos y, al mismo tiempo, animar las secuencias.

El brillo se controla con **PWM** a 1 kHz. El ciclo útil (`duty_u16`, de 0 a 65535) se calcula a partir del porcentaje deseado:

```python
def brillo(pct):
    led.duty_u16(int(65535 * pct / 100))
```

| Comando | Ciclo útil |
|---|---|
| `F` | 30 % → 19660 |
| `V` | 70 % → 45874 |
| `P` | 100 % → 65535 |

Las secuencias se ejecutan con temporizadores basados en `time.ticks_ms()`, sin usar `sleep` largos:

- **Secuencia 1 (`U`):** el brillo sube de 0 a 100 % y vuelve a bajar, en un ciclo de unos 2 segundos.
- **Secuencia 2 (`D`):** el LED se enciende y apaga cada 150 ms.

---

# Ejecución del proyecto

Todos los comandos se escriben en la terminal de **Visual Studio Code (PowerShell)**.

## 1. Entrar a la carpeta

```powershell
cd "actividad 4"
```

## 2. Instalar las librerías del computador

```powershell
python -m pip install mediapipe opencv-python pyserial mpremote
```

## 3. Identificar el puerto de la ESP32

```powershell
python -m mpremote connect list
```

En este montaje la ESP32 quedó en **COM8**.

## 4. Cargar el programa en la ESP32

```powershell
python -m mpremote connect COM8 fs cp .\main.py :main.py
python -m mpremote connect COM8 reset
```

`main.py` arranca automáticamente cada vez que la ESP32 se enciende o se reinicia.

## 5. Configurar el puerto en el programa del computador

En `ACTIVIDAD4.py`, el puerto debe coincidir con el de la ESP32:

```python
esp32 = serial.Serial('COM8', 115200, timeout=1)
print("Conectado al COM8. Esperando inicio del ESP32...")
```

## 6. Ejecutar

```powershell
python ACTIVIDAD4.py
```

Se abre la ventana de la cámara. Al hacer un gesto frente a ella, la terminal muestra el comando enviado (por ejemplo, `Enviado: P`) y el LED cambia. Para salir, se presiona **q** en la ventana de la cámara.

---

# Secuencia de operación

1. El usuario hace un gesto frente a la cámara.
2. OpenCV captura el fotograma.
3. MediaPipe reconoce el gesto y su confianza.
4. `ACTIVIDAD4.py` traduce el gesto a una letra.
5. La letra se envía a la ESP32 por USB serie.
6. La ESP32 lee la letra en `main.py`.
7. La ESP32 ajusta el PWM del LED o ejecuta la secuencia correspondiente.

---

# Solución de problemas

| Problema | Causa | Solución |
|---|---|---|
| `could not open port 'COM5'` | El puerto del código no es el de la ESP32 | Cambiar `'COM5'` por el puerto real (`COM8`) en `ACTIVIDAD4.py` |
| `Error al abrir el puerto` / puerto ocupado | Otra terminal, Thonny o `mpremote repl` usa el puerto | Cerrar el otro programa antes de ejecutar |
| El LED no enciende | LED invertido o pin equivocado | Pata larga hacia la resistencia y GPIO4 (rotulado G4 o IO4); pata corta a GND |
| El LED no cambia al repetir un gesto | El programa solo envía cuando el gesto cambia | Hacer otro gesto en medio |
| No se encuentra `gesture_recognizer.task` | Falta el modelo en la carpeta | Copiar el archivo junto a `ACTIVIDAD4.py` |
| Mensajes `W0000`, `I0000` o `WARNING` en la terminal | Avisos normales de MediaPipe y TensorFlow | No son errores; se pueden ignorar |

---

# Comunicaciones y tecnologías utilizadas

| Tecnología | Función |
|---|---|
| OpenCV | Captura de video y visualización |
| MediaPipe Gesture Recognizer | Reconocimiento de gestos de la mano |
| USB Serial (115200 baudios) | Envío de comandos del PC a la ESP32 |
| MicroPython | Programación de la ESP32 |
| PWM | Control del brillo del LED |

---

## Evidencia

El siguiente video muestra el funcionamiento completo del sistema:

[▶️ Video demostrativo Actividad 4](https://drive.google.com/file/d/1i0XzKrJxuER7FA7q86VHidxKOjmhh-tu/view?usp=sharing)

---

# Conclusión

Se integró un sistema de visión por computador con un microcontrolador para controlar un actuador físico mediante gestos de la mano. El computador se encarga del procesamiento pesado (captura de video y reconocimiento con MediaPipe), mientras que la ESP32 recibe comandos simples por USB serie y controla el LED con PWM.

Enviar solo el comando cuando el gesto cambia mantiene la comunicación liviana, y la lectura no bloqueante del puerto en la ESP32 le permite recibir órdenes nuevas mientras ejecuta las secuencias de luz. El resultado es una interfaz sin contacto, natural e intuitiva, que demuestra cómo la inteligencia artificial puede controlar dispositivos del mundo real.
