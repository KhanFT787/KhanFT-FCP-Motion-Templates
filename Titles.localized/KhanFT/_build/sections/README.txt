KhanFT section cards - build sources (Oct 2026)
Generated .moti/.motr files are built by these scripts from Motion-saved skeletons
(../skel.moti.txt for titles, ../tskel.motr.txt for transitions; rename to .moti/.motr as skel.moti / tskel.motr next to kft.py).
Other inputs: sec1.moti / words1.moti / cards1.moti = copies of KhanFT Section Type 1 / Words Type 1 / Cards Type 1,
icons/ = Cards Type 1 Media icons, Grain.png = Section Type 1 Media, orbit/gen.py renders the Ledger Orbit objects.
Run: python3 build_<card>.py  (OUTDIR env var = output folder)
