# KhanFT Section Type 6 - Colour Motion: Colour Field plus a subtle moving layer between the background and the content.
# Built from build_colour_field.py (so it keeps every Colour Field feature); the moving layer's ids come from their own band.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
src = open(os.path.join(HERE, 'build_colour_field.py')).read()

def rep(a, b):
    global src
    assert src.count(a) == 1, a
    src = src.replace(a, b)

rep("c = Card('KhanFT Section Type 3 – Colour Field'); d = c.d", "c = Card('KhanFT Section Type 6 – Colour Motion'); d = c.d")
rep("P(VIG, './1/200/202', 'Vignette'); P(GR, './1/200/202', 'Grain')\n",
    "P(VIG, './1/200/202', 'Vignette'); P(GR, './1/200/202', 'Grain')\n"
    "from motion_layer import motion_layer\nmotion, motion_pub = motion_layer(c, d, FW, FH); motion_pub(P)\n")
rep("children=grain + vig + content + backgrounds,", "children=grain + vig + content + motion + backgrounds,")
rep("thumb='/tmp/claude-0/-home-claude/14ea8a7a-73b0-5e09-b753-32cc7b5c2796/scratchpad/chk_2.png'",
    "thumb=" + repr(os.path.join(HERE, 'motion', 'thumb_type6.png')))
exec(compile(src, 'build_colour_motion', 'exec'), {'__file__': os.path.join(HERE, 'build_colour_field.py'), '__name__': '__main__'})
