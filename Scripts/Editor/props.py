"""Lists python attribute names of a class matching a substring (CLASS and PATTERN below). Log prefix [Props]."""
import unreal
CLASS, PATTERN = "MaterialProperty", "mp_"
cls = getattr(unreal, CLASS)
unreal.log("[Props] " + ", ".join(n for n in dir(cls) if PATTERN in n.lower() or PATTERN in n.upper()))
