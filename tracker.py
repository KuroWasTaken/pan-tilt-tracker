# tracker.py — Détection de cible et calcul d'erreur angulaire
# Quentin Jallais · Pan-Tilt Tracker · 2026
# Exécuté sur OpenMV Cam H7

import sensor
import time
import uart_com

# ── Configuration caméra ──────────────────────────────────────────
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)   # 320x240
sensor.set_vflip(False)
sensor.skip_frames(time=2000)

FRAME_W = 320
FRAME_H = 240
CENTER_X = FRAME_W // 2
CENTER_Y = FRAME_H // 2

# Seuil couleur cible (rouge vif en LAB)
THRESHOLD_RED = [(30, 80, 40, 80, 10, 60)]

# ── Paramètres de contrôle ────────────────────────────────────────
DEADZONE_PX   = 8       # pixels — zone morte centrale
MIN_AREA      = 400     # px² — filtre les petits blobs parasites

clock = time.clock()

# ── Boucle principale ─────────────────────────────────────────────
while True:
    clock.tick()
    img = sensor.snapshot()

    blobs = img.find_blobs(
        THRESHOLD_RED,
        pixels_threshold=MIN_AREA,
        area_threshold=MIN_AREA,
        merge=True
    )

    if blobs:
        # Blob le plus grand = cible principale
        target = max(blobs, key=lambda b: b.area())

        cx = target.cx()
        cy = target.cy()

        # Erreur en pixels par rapport au centre frame
        err_x = cx - CENTER_X   # > 0 → cible à droite
        err_y = cy - CENTER_Y   # > 0 → cible en bas

        # Dessin debug
        img.draw_cross(cx, cy, color=(255, 0, 0))
        img.draw_rectangle(target.rect(), color=(0, 255, 0))

        # Envoi seulement si hors zone morte
        if abs(err_x) > DEADZONE_PX or abs(err_y) > DEADZONE_PX:
            uart_com.send_error(err_x, err_y)

    # FPS console debug
    # print(clock.fps())



# controller.py — Envoi des commandes de correction via UART
# Quentin Jallais · Pan-Tilt Tracker · 2026

import struct

try:
    from machine import UART
    uart = UART(3, baudrate=115200, timeout=10)
    OPENMV_MODE = True
except ImportError:
    import serial
    uart = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.01)
    OPENMV_MODE = False

# ── Protocole trame ───────────────────────────────────────────────
# Format : [0xAA][err_x : int16][err_y : int16][0x55]
# Total  : 6 octets par trame

HEADER = b'\xAA'
FOOTER = b'\x55'

# Gain proportionnel (steps/pixel)
KP_PAN  = 0.45
KP_TILT = 0.40

# Limites mécaniques (steps par commande)
MAX_STEP = 80


def _clamp(value: float, limit: int) -> int:
    return max(-limit, min(limit, int(value)))


def send_error(err_x: int, err_y: int) -> None:
    """
    Convertit l'erreur pixel en nombre de steps moteur
    et envoie la trame UART.
    """
    steps_pan  = _clamp(err_x * KP_PAN,  MAX_STEP)
    steps_tilt = _clamp(err_y * KP_TILT, MAX_STEP)

    frame = HEADER + struct.pack('>hh', steps_pan, steps_tilt) + FOOTER

    if OPENMV_MODE:
        uart.write(frame)
    else:
        uart.write(frame)


def send_home() -> None:
    """Commande retour position neutre (0, 0)."""
    send_error(0, 0)
