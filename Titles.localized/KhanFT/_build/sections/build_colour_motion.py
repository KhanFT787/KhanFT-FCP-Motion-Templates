# KhanFT Section Type 6 - Colour Motion (calm layers: rings, sweeps, glow, bokeh ...)
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from colour_motion_base import build
build('KhanFT Section Type 6 – Colour Motion', os.path.join(HERE, 'motion', 'thumb_type6.png'), "layer=3, speed='Fast', kind='calm'")
