"""Freeze source-only delivery documentation and receipts. No UE/compiler execution."""
from pathlib import Path
import hashlib,json
here=Path(__file__).resolve().parent
root=here.parents[4]
cpp=root/'Source/OneBossFight/Player/RPGBossHealPunishAdapters.cpp'
s=cpp.read_text(encoding='utf-8').replace('CastChecked < URPGBossHealPunish > (','CastChecked<URPGBossHealPunish>(')
cpp.write_text(s,encoding='utf-8')
binding=root/'Source/OneBossFight/Player/RPGEncounterBinding.cpp'
s=binding.read_text(encoding='utf-8').replace('if (!RPGBossHealPunishAdapters::ValidateHealPunish(D.HealPunish,PunishError)) { Result.Fail(PunishError); } // C265 authored structure; no move/socket resolution','// C265 authored structure; no move/socket resolution.\n\tif (!RPGBossHealPunishAdapters::ValidateHealPunish(D.HealPunish, PunishError))\n\t{\n\t\tResult.Fail(PunishError);\n\t}')
binding.write_text(s,encoding='utf-8')
summary='DD22 source-only handoff (C265/C266/C267,2026-10-29): typed HealPunish14-field profile, compiler validation/copy and isolated adapter with six UNRUN regression sources. Five-file delta200->203 Source,198 prior files unchanged. Codex/DD22/DELIVERY_TO_CLAUDE.md; Claude SOURCE REVIEW PENDING. No build/UHT/engine run. Combined DD21+DD22 execution needs Claude exact release.'
for n in ['TASKS.md','TEST_PLAN.md','DECISIONS.md']:
    p=root/'Documentation'/n
    with p.open('a',encoding='utf-8') as f:f.write('\n\n'+summary+'\n')
ki=root/'Documentation/KNOWN_ISSUES.md'
with ki.open('a',encoding='utf-8') as f:
    f.write('\n\nDD22 C265/C267 source-only residual: authored numeric ceilings/floor do not constrain external world coordinates/time. Dist/FlightTime analysis assumes finite ordinary world geometry; any arena bounds are external assumptions, not validated profile fields. FeetZ can overflow during double-to-float narrowing before bounded AimHeight addition. Native A5 and player drink montage remain hardcoded/unresolved; socket names prove syntax only, not existence/load/fallback fit. No heal event, projectile, hit/damage or serialized/Details proof. See Codex/DD22/NATIVE_ARITHMETIC_AUDIT.md; six test sources UNRUN.\nC266 accepted DD19/DD20 arithmetic residual (identifier KI-126 already belongs to authoring-toolkit history; preserved without overwriting): Bleed intermediate threshold sum may overflow before Min returns finite cap; buildup accumulation/attribute narrowing and LowSweep external geometry remain open. No correction to DD19/DD20 accepted source was ordered or made.\n')
current=root/'Docs/BossCombatReview/Execution/Codex/CURRENT_TASK.md'
old=current.read_text(encoding='utf-8')
current.write_text('CURRENT IMPLEMENTER C265/C266/C267: DD21 source accepted C266; DD22 source delivered for Claude review. Live203 Source includes both packages, no build/UHT/engine run for either. Combined one-build/focusedShockwave/focusedHealPunish/full gate is a lead plan, not execution release. DD22/DELIVERY_TO_CLAUDE.md controls current delivery.\n\n'+old,encoding='utf-8')
body='''# DD22 HealPunish source handoff — C265/C266/C267

SOURCE ONLY. Three new adapter/test files, ONLY existing Binding.h/.cpp edited. Baseline is frozen DD21 source200: full203 Source manifest,198 prior files unchanged, exact five-file diff, preimages, five pins and byte-identical Review copies. DD21 adapter/tests and all native runtime files unchanged. No build/UHT/engine/automation/git operation.

FRPGHealPunishConfig has all14 native authored fields/defaults; ten floats finite first in header order, then C265 domains in header order. Cap1e6 on nine magnitude fields (AimHeight signed); Damage finite>=0 without ceiling; FlightTime>=0.05; MaxRange>MinRange; equal speed endpoints accepted. Socket array nonempty and each name non-None/no whitespace/control, no regex/uniqueness/existence rule. Array validation precedes signed AimHeight domain checks. Shared compiler validator runs before config publication; compiler copies the array by value. Callback checks exact class, destruction, registration, BeginPlay and owner before whole-record validation, then copies all14 fields. Plan has native instance name and14 explicit required paths; remains UNWIRED.

Six test sources HealPunish.{Assign,Validation,Isolation,Rejections,Compile,Authoring}, all UNRUN. Thirty nonfinite cases plus domain/order/nextafter/ceiling edges, FLT_MAX Damage, flight floor and sub-1 factors, equal speeds, signed AimHeight, duplicate/punctuation socket names, array value-copy isolation, populated-output clearing on compiler rejection, lifecycle refusal/no partial writes, reflection/defaults and unchanged runtime flags/counters. No native HealPunish BeginPlay/Tick/heal event/CancelAll, javelin creation/launch, tracker or damage resolver call. ComponentBegunPlay guard remains source-only. MinRange=cap cannot form a valid MaxRange>MinRange<=cap record: largest valid pair uses predecessor(cap),Max=cap; equal cap reports relational refusal.

NATIVE_ARITHMETIC_AUDIT.md covers distance/FlightTime, double worldtime+Cooldown and FeetZ+AimHeight with source types/lines and explicit external-input limits. No claim arena coordinates are bounded by this profile. Release distance is not assumed to remain in admission range. Extreme double geometry/narrowing/NaN risks remain external; A5/drink montage hardcodes and socket/bone resolution remain UNRESOLVED. No gameplay/serialized authoring/networking/cook/package/all83 proof.

Pre-delivery self-review corrected a generator word substitution that had changed AimHeight to AimHfourteen in the uncompiled test source. PreReview copy preserves those bytes; generator now uses word boundaries. This was caught before any compiler/run, not a failed engine attempt. DD22 adapter formatting now follows C266 spacing/one-statement style; frozen DD21 files untouched. Documentation records DD22 pending limits and C266 DD19/DD20 residual without overwriting the existing KI-126 authoring entry.

Source capture exit0 establishes file integrity only, not C++ or Unreal success. Please independently review these bytes, then issue exact combined DD21+DD22 execution release per C266 if accepted. No source edits or run will be inferred from the proposed gate.
'''
(here/'DELIVERY_TO_CLAUDE.md').write_text(body,encoding='utf-8')
print('Delivery and documentation prepared; source capture must run next.')
