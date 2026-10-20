"""Logs bounds of the imported Boss01 body and sword by two APIs. Log prefix [Bounds]."""
import unreal

body = unreal.load_asset("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body")
b = body.get_bounds()
unreal.log("[Bounds] body get_bounds origin %s extent %s" % (b.origin, b.box_extent))
ib = body.get_imported_bounds() if hasattr(body, "get_imported_bounds") else None
unreal.log("[Bounds] body imported bounds %s" % ib)
sword = unreal.load_asset("/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword")
bb = sword.get_bounding_box()
unreal.log("[Bounds] sword bbox min %s max %s" % (bb.min, bb.max))
sb = sword.get_bounds()
unreal.log("[Bounds] sword get_bounds extent %s" % sb.box_extent)
