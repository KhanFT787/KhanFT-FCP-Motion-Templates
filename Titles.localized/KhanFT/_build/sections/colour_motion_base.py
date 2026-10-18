# Builds a Colour Motion card: the Colour Field card (build_colour_field.py, unchanged) plus a subtle moving layer
# between the background and the content, with Khan's chosen defaults (18 Oct 2026). Used by Types 6, 7 and 8.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)


def build(card, thumb, motion_args):
    src = open(os.path.join(HERE, 'build_colour_field.py')).read()
    def rep(a, b):
        nonlocal src
        assert src.count(a) == 1, a
        src = src.replace(a, b)
    rep("c = Card('KhanFT Section Type 3 – Colour Field'); d = c.d", f"c = Card({card!r}); d = c.d")
    rep("P(VIG, './1/200/202', 'Vignette'); P(GR, './1/200/202', 'Grain')\n",
        "P(VIG, './1/200/202', 'Vignette'); P(GR, './1/200/202', 'Grain')\n"
        f"from motion_layer import motion_layer\nmotion, motion_pub = motion_layer(c, d, FW, FH, {motion_args}); motion_pub(P)\n")
    rep("children=grain + vig + content + backgrounds,", "children=grain + vig + content + motion + backgrounds,")
    rep("thumb='/tmp/claude-0/-home-claude/14ea8a7a-73b0-5e09-b753-32cc7b5c2796/scratchpad/chk_2.png'", "thumb=" + repr(thumb))
    # defaults
    rep("W_PRE = d.w_popup('Colour Preset', [p[0] for p in PRESETS], 0)", "W_PRE = d.w_popup('Colour Preset', [p[0] for p in PRESETS], 1)")   # Teal
    rep("children=a+m+b, op=1 if i == 0 else 0,", "children=a+m+b, op=1 if i == 1 else 0,")
    rep("c.text_extras('Counter', CNT, cnt, pad=(50, 26))", "c.text_extras('Counter', CNT, cnt, pad=(50, 26), float_on=True, float_speed=0.4)")
    rep("c.text_extras('Title', TTL, ttl, pad=(90, 50))", "c.text_extras('Title', TTL, ttl, pad=(90, 50), box_on=True, float_on=True, float_speed=0.4)")
    rep("c.text_out('Counter', CNTO, 30, seq=CNT_SEQ[1], lead=0.3)", "c.text_out('Counter', CNTO, 30, seq=CNT_SEQ[1], lead=0.3, default='Drop')")
    rep("c.text_out('Title', TTLO, 45, seq=TTL_SEQ[1], lead=0.4)", "c.text_out('Title', TTLO, 45, seq=TTL_SEQ[1], lead=0.4, default='Drop')")
    rep("c.icon_block(px=0, py=640, size=0.85, t0=0.7, icon_lead=0.2)", "c.icon_block(px=0, py=640, size=0.85, t0=0.7, icon_lead=0.2, show=True, icon_out='Drop')")
    exec(compile(src, card, 'exec'), {'__file__': os.path.join(HERE, 'build_colour_field.py'), '__name__': '__main__'})
