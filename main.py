# main.py  -  ESP32 / ESP32-S3 (MicroPython)
# Actividad 4: recibe por USB el comando que envia ACTIVIDAD4.py (MediaPipe)
# y controla UN LED con PWM.
#
#   Comando  Gesto         Accion del LED
#   F        Closed_Fist   brillo al 30 %
#   V        Victory       brillo al 70 %
#   P        Open_Palm     brillo al 100 %
#   U        Thumb_Up      secuencia 1: "respiracion" (sube y baja el brillo)
#   D        Thumb_Down    secuencia 2: parpadeo rapido
#
# Montaje: GPIO4 -> resistencia 220 ohm -> pata larga (+) del LED
#          pata corta (-) del LED -> GND

import sys
import time
import select
from machine import Pin, PWM

PIN_LED = 4
led = PWM(Pin(PIN_LED), freq=1000, duty_u16=0)


def brillo(pct):
    """Brillo del LED en porcentaje (0 a 100)."""
    led.duty_u16(int(65535 * pct / 100))


# Lectura sin bloqueo del puerto USB
lector = select.poll()
lector.register(sys.stdin, select.POLLIN)

modo = None
paso = 0
t_paso = time.ticks_ms()
brillo(0)
print("ESP32 lista. Esperando gestos (F, V, P, U, D)")

while True:
    # 1) Llego un comando desde ACTIVIDAD4.py?
    if lector.poll(0):
        c = sys.stdin.read(1)
        if c in ("F", "V", "P", "U", "D"):
            modo = c
            paso = 0
            t_paso = time.ticks_ms()
            if c == "F":
                brillo(30)
            elif c == "V":
                brillo(70)
            elif c == "P":
                brillo(100)
            print("OK", c)

    # 2) Secuencias (se animan sin dejar de leer comandos)
    ahora = time.ticks_ms()
    if modo == "U" and time.ticks_diff(ahora, t_paso) >= 20:
        # respiracion: el brillo sube de 0 a 100 % y baja, en unos 2 s
        t_paso = ahora
        fase = paso % 100
        brillo(fase * 2 if fase < 50 else (100 - fase) * 2)
        paso += 1
    elif modo == "D" and time.ticks_diff(ahora, t_paso) >= 150:
        # parpadeo rapido: encendido / apagado cada 150 ms
        t_paso = ahora
        brillo(100 if paso % 2 == 0 else 0)
        paso += 1

    time.sleep_ms(5)