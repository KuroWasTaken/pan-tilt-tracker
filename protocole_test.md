# Protocole de Validation — Tourelle Pan-Tilt #

## Objectif

Valider les performances de la boucle de contrôle du système de suivi autonome
sur trois critères : latence, précision angulaire et stabilité.

## Matériel requis

- Tourelle Pan-Tilt assemblée (NEMA 17 + A4988 + courroies GT2) OU moteur servo pour essai
- OpenMV Cam H7 montée sur la tourelle
- Cible : carré rouge 10×10 cm sur fond blanc
- PC avec terminal série (115200 bauds) pour log UART
- Règle graduée + rapporteur pour mesure angulaire
- Chronomètre / oscilloscope logiciel (ex. PulseView)

---

## Test 1 — Latence de la boucle de contrôle

### Objectif
Mesurer le délai entre la détection visuelle de la cible et le premier mouvement moteur.

### Méthode
1. Placer la cible hors champ, puis la faire apparaître brusquement
2. Timestamper via UART l'instant de détection (message envoyé) et l'instant
   de réception côté contrôleur
3. Répéter **20 fois**, calculer moyenne et écart-type

### Critère d'acceptation
| Métrique | Valeur cible |
|---|---|
| Latence moyenne | < 80 ms |
| Écart-type | < 15 ms |

---

## Test 2 — Précision de suivi angulaire

### Objectif
Vérifier que la tourelle positionne la cible dans la zone morte centrale (±8 px).

### Méthode
1. Placer la cible à des offsets connus : ±30°, ±15°, ±5° (pan et tilt)
2. Laisser la boucle se stabiliser (timeout 3 s)
3. Relever l'erreur résiduelle en pixels dans le flux caméra

### Critère d'acceptation
| Position cible | Erreur résiduelle max |
|---|---|
| ±30° | ≤ 10 px |
| ±15° | ≤ 6 px  |
| ±5°  | ≤ 4 px  |

---

## Test 3 — Stabilité en régime permanent

### Objectif
S'assurer qu'il n'y a pas d'oscillations autour du point d'équilibre.

### Méthode
1. Centrer la cible manuellement
2. Observer le flux caméra pendant **30 secondes**
3. Enregistrer la position (cx, cy) toutes les 100 ms via terminal

### Critère d'acceptation
- Pas d'oscillations > ±5 px en régime permanent
- Pas de décrochage (perte de suivi > 1 s)

---

## Conditions de test

- Éclairage : intérieur fluorescent 500 lux
- Distance cible : 80 cm
- Température ambiante : 20–25 °C
