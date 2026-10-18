# KhanFT Section Type 8 - Graphic Motion (wire globe, wire cube, perspective floor, parallax hills, orbits, scan line)
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from colour_motion_base import build
build('KhanFT Section Type 8 – Graphic Motion', os.path.join(HERE, 'motion', 'thumb_type8.png'), "layer=0, speed='Normal', kind='graphic'")
