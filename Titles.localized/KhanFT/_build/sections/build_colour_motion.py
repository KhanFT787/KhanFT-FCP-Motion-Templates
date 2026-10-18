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
# defaults (Khan's chosen look, 18 Oct 2026)
rep("W_PRE = d.w_popup('Colour Preset', [p[0] for p in PRESETS], 0)", "W_PRE = d.w_popup('Colour Preset', [p[0] for p in PRESETS], 1)")   # Teal
rep("children=a+m+b, op=1 if i == 0 else 0,", "children=a+m+b, op=1 if i == 1 else 0,")
rep("c.text_extras('Counter', CNT, cnt, pad=(50, 26))", "c.text_extras('Counter', CNT, cnt, pad=(50, 26), float_on=True, float_speed=0.4)")
rep("c.text_extras('Title', TTL, ttl, pad=(90, 50))", "c.text_extras('Title', TTL, ttl, pad=(90, 50), box_on=True, float_on=True, float_speed=0.4)")
rep("c.text_out('Counter', CNTO, 30, seq=CNT_SEQ[1])", "c.text_out('Counter', CNTO, 30, seq=CNT_SEQ[1], default='Drop')")
rep("c.text_out('Title', TTLO, 45, seq=TTL_SEQ[1])", "c.text_out('Title', TTLO, 45, seq=TTL_SEQ[1], default='Drop')")
rep("c.icon_block(px=0, py=640, size=0.85, t0=0.7)", "c.icon_block(px=0, py=640, size=0.85, t0=0.7, show=True, icon_out='Drop')")
rep("motion_layer(c, d, FW, FH)", "motion_layer(c, d, FW, FH, layer=3, speed='Fast')")
exec(compile(src, 'build_colour_motion', 'exec'), {'__file__': os.path.join(HERE, 'build_colour_field.py'), '__name__': '__main__'})
