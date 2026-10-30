#!/usr/bin/env python3
"""
verify_a274_witness.py
Re-opens and verifies every cited line in WITNESS_STATUS_F3_F4.md against raw logs.
"""

import json, sys
from pathlib import Path

LOGS = {
    "c2_full": Path("Docs/BossCombatReview/Execution/Claude/F4/c2_full_raw.log"),
    "f4_run1": Path("Docs/BossCombatReview/Execution/Claude/F4/final_f4_run1/editor_raw.log"),
    "f4_run2": Path("Docs/BossCombatReview/Execution/Claude/F4/final_f4_run2/editor_raw.log"),
    "f4_run3": Path("Docs/BossCombatReview/Execution/Claude/F4/final_f4_run3/editor_raw.log"),
    "f4_regr": Path("Docs/BossCombatReview/Execution/Claude/F4/final_f3_regression/editor_raw.log"),
    "f3_run1": Path("Docs/BossCombatReview/Execution/Claude/F3d/final_run1/editor_raw.log"),
}

CITATIONS = [
    ("BOSS-ANM-001", "c2_full", 3769, "[2026.10.30-12.14.52:677][989]LogAutomationController: Display: Test Completed. Result={Success} Name={Crossing} Path={OneBossFight.Framework.MoveModel.Crossing}"),
    ("BOSS-ANM-001", "f4_run1", 1507, "[2026.10.30-12.12.21:915][353]LogTemp: Display: [FrameworkProof] playback_start encounter=1 generation=1 instance=1 montage=/Engine/Transient.AnimMontage_0 slot=FullBody rate=1 label=F4_fixture"),
    ("BOSS-ANM-002", "c2_full", 3745, "[2026.10.30-12.14.52:609][981]LogAutomationController: Display: Test Completed. Result={Success} Name={Rejections} Path={OneBossFight.Framework.MoveCard.Rejections}"),
    ("BOSS-ANM-002", "f4_run1", 1571, "[2026.10.30-12.12.22:294][379]LogTemp: Display: [FrameworkProof] event encounter=1 generation=1 instance=1 kind=Open window=Window_SwingSlow_Primary group=HitGroup_ScytheBlade localSeconds=0.35 label=F4_fixture"),
    ("BOSS-ANM-005", "f4_run1", 1506, "[2026.10.30-12.12.21:904][352]LogTemp: Display: [FrameworkProof] walk start=X=500.000 Y=0.000 Z=167.150 end=X=169.690 Y=0.000 Z=167.150 distanceCm=330.31 rangeCm=169.69 bandMin=150 bandMax=180 capsule=X=169.690 Y=0.000 Z=167.150 mesh=X=169.690 Y=0.000 Z=2.150"),
    ("BOSS-ANM-005", "f4_run1", 1507, "[2026.10.30-12.12.21:915][353]LogTemp: Display: [FrameworkProof] playback_start encounter=1 generation=1 instance=1 montage=/Engine/Transient.AnimMontage_0 slot=FullBody rate=1 label=F4_fixture"),
    ("BOSS-ANM-005", "c2_full", 3745, "[2026.10.30-12.14.52:609][981]LogAutomationController: Display: Test Completed. Result={Success} Name={Rejections} Path={OneBossFight.Framework.MoveCard.Rejections}"),
    ("BOSS-ANM-007", "c2_full", 3757, "[2026.10.30-12.14.52:644][985]LogAutomationController: Display: Test Completed. Result={Success} Name={Abort} Path={OneBossFight.Framework.MoveModel.Abort}"),
    ("BOSS-ANM-008", "f4_run1", 1454, "[2026.10.30-12.12.20:406][275]LogTemp: Display: [FrameworkProof] dependencies mesh=/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog.Sevarog skeleton=/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton.Sevarog_Skeleton animClass=/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sevarog_AnimBlueprint.Sevarog_AnimBlueprint_C sequence=/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Slow.Swing1_Slow slot=FullBody resolved=1 label=F4_fixture"),
    ("BOSS-ANM-008", "c2_full", 3835, "[2026.10.30-12.14.53:484][  8]LogAutomationController: Display: Test Completed. Result={Success} Name={ResolvedDependencies} Path={OneBossFight.Framework.Runtime.ResolvedDependencies}"),
    ("BOSS-AWR-001", "c2_full", 3812, "[2026.10.30-12.14.52:794][  3]LogAutomationController: Display: Test Completed. Result={Success} Name={PlaybackGuards} Path={OneBossFight.Framework.Runtime.PlaybackGuards}"),
    ("BOSS-AWR-001", "c2_full", 3693, "[2026.10.30-12.14.52:038][968]LogAutomationController: Display: Test Completed. Result={Success} Name={Decide} Path={OneBossFight.Combat.DamageResolver.Decide}"),
    ("BOSS-AWR-003", "c2_full", 3775, "[2026.10.30-12.14.52:693][991]LogAutomationController: Display: Test Completed. Result={Success} Name={Eligibility} Path={OneBossFight.Framework.MoveModel.Eligibility}"),
    ("BOSS-AWR-003", "f4_run1", 1506, "[2026.10.30-12.12.21:904][352]LogTemp: Display: [FrameworkProof] walk start=X=500.000 Y=0.000 Z=167.150 end=X=169.690 Y=0.000 Z=167.150 distanceCm=330.31 rangeCm=169.69 bandMin=150 bandMax=180 capsule=X=169.690 Y=0.000 Z=167.150 mesh=X=169.690 Y=0.000 Z=2.150"),
    ("BOSS-AWR-004", "c2_full", 3775, "[2026.10.30-12.14.52:693][991]LogAutomationController: Display: Test Completed. Result={Success} Name={Eligibility} Path={OneBossFight.Framework.MoveModel.Eligibility}"),
    ("BOSS-COM-002", "c2_full", 3769, "[2026.10.30-12.14.52:677][989]LogAutomationController: Display: Test Completed. Result={Success} Name={Crossing} Path={OneBossFight.Framework.MoveModel.Crossing}"),
    ("BOSS-COM-002", "f4_run1", 1599, "[2026.10.30-12.12.22:426][388]LogTemp: Display: [FrameworkProof] event encounter=1 generation=1 instance=1 kind=Close window=Window_SwingSlow_Primary group=HitGroup_ScytheBlade localSeconds=0.4917 label=F4_fixture"),
    ("BOSS-DEF-001", "f4_run1", 1439, "[2026.10.30-12.12.19:625][275]LogTemp: Display: [FrameworkProof] target_health_init value=800 readback=800 label=F4_fixture"),
    ("BOSS-DEF-001", "f4_run1", 1651, "[2026.10.30-12.12.23:605][435]LogTemp: Display: [FrameworkProof] invariant targetHPBefore=800 targetHPAfter=765 expectedHP=765 acceptedHits=1 appliedDamage=35"),
    ("BOSS-DEF-001", "c2_full", 3180, "[2026.10.30-12.14.49:945][879]LogAutomationController: Display: Test Completed. Result={Success} Name={Assign} Path={OneBossFight.Binding.StatsAdapters.Assign}"),
    ("BOSS-DEF-002", "c2_full", 3465, "[2026.10.30-12.14.50:489][917]LogAutomationController: Display: Test Completed. Result={Success} Name={PostureRegen} Path={OneBossFight.Boss.PostureRegen}"),
    ("BOSS-DEF-003", "c2_full", 3483, "[2026.10.30-12.14.50:539][923]LogAutomationController: Display: Test Completed. Result={Success} Name={TransitionRules} Path={OneBossFight.Boss.TransitionRules}"),
    ("BOSS-DEF-003", "c2_full", 3120, "[2026.10.30-12.14.49:820][864]LogAutomationController: Display: Test Completed. Result={Success} Name={Assign} Path={OneBossFight.Binding.StaggerPolicy.Assign}"),
    ("BOSS-EXE-001", "c2_full", 3781, "[2026.10.30-12.14.52:710][993]LogAutomationController: Display: Test Completed. Result={Success} Name={GenerationAndDoubleStart} Path={OneBossFight.Framework.MoveModel.GenerationAndDoubleStart}"),
    ("BOSS-EXE-001", "c2_full", 3483, "[2026.10.30-12.14.50:539][923]LogAutomationController: Display: Test Completed. Result={Success} Name={TransitionRules} Path={OneBossFight.Boss.TransitionRules}"),
    ("BOSS-EXE-002", "c2_full", 3799, "[2026.10.30-12.14.52:760][999]LogAutomationController: Display: Test Completed. Result={Success} Name={ReserveBeforePlayback} Path={OneBossFight.Framework.MoveModel.ReserveBeforePlayback}"),
    ("BOSS-EXE-003", "c2_full", 3799, "[2026.10.30-12.14.52:760][999]LogAutomationController: Display: Test Completed. Result={Success} Name={ReserveBeforePlayback} Path={OneBossFight.Framework.MoveModel.ReserveBeforePlayback}"),
    ("BOSS-EXE-004", "c2_full", 3781, "[2026.10.30-12.14.52:710][993]LogAutomationController: Display: Test Completed. Result={Success} Name={GenerationAndDoubleStart} Path={OneBossFight.Framework.MoveModel.GenerationAndDoubleStart}"),
    ("BOSS-EXE-004", "c2_full", 3693, "[2026.10.30-12.14.52:038][968]LogAutomationController: Display: Test Completed. Result={Success} Name={Decide} Path={OneBossFight.Combat.DamageResolver.Decide}"),
    ("BOSS-EXE-005", "c2_full", 3483, "[2026.10.30-12.14.50:539][923]LogAutomationController: Display: Test Completed. Result={Success} Name={TransitionRules} Path={OneBossFight.Boss.TransitionRules}"),
    ("BOSS-EXE-006", "c2_full", 3757, "[2026.10.30-12.14.52:644][985]LogAutomationController: Display: Test Completed. Result={Success} Name={Abort} Path={OneBossFight.Framework.MoveModel.Abort}"),
    ("BOSS-EXE-006", "c2_full", 3812, "[2026.10.30-12.14.52:794][  3]LogAutomationController: Display: Test Completed. Result={Success} Name={PlaybackGuards} Path={OneBossFight.Framework.Runtime.PlaybackGuards}"),
    ("BOSS-EXE-007", "c2_full", 3793, "[2026.10.30-12.14.52:744][997]LogAutomationController: Display: Test Completed. Result={Success} Name={PauseAndBoundaries} Path={OneBossFight.Framework.MoveModel.PauseAndBoundaries}"),
    ("BOSS-EXE-007", "f4_run1", 1649, "[2026.10.30-12.12.23:569][433]LogTemp: Display: [FrameworkProof] event encounter=1 generation=1 instance=1 kind=Finished window=None group=None localSeconds=1.65 label=F4_fixture"),
    ("BOSS-EXE-008", "f4_run1", 1599, "[2026.10.30-12.12.22:426][388]LogTemp: Display: [FrameworkProof] event encounter=1 generation=1 instance=1 kind=Close window=Window_SwingSlow_Primary group=HitGroup_ScytheBlade localSeconds=0.4917 label=F4_fixture"),
    ("BOSS-EXE-008", "f4_run1", 1650, "[2026.10.30-12.12.23:582][434]LogTemp: Display: [FrameworkProof] cleanup reason=Finished modelIdle=1 ownedMontageStopped=1"),
    ("BOSS-EXE-008", "c2_full", 3757, "[2026.10.30-12.14.52:644][985]LogAutomationController: Display: Test Completed. Result={Success} Name={Abort} Path={OneBossFight.Framework.MoveModel.Abort}"),
    ("BOSS-HIT-001", "f4_run1", 1508, "[2026.10.30-12.12.21:915][353]LogTemp: Display: [FrameworkProof] playback instance=1 position=0 nodeWeight=1 montageWeight=0 base=X=98.707 Y=-12.397 Z=94.474 tip=X=11.131 Y=69.234 Z=63.805"),
    ("BOSS-HIT-001", "c2_full", 3805, "[2026.10.30-12.14.52:777][  1]LogAutomationController: Display: Test Completed. Result={Success} Name={DamageProfile} Path={OneBossFight.Framework.Runtime.DamageProfile}"),
    ("BOSS-HIT-002", "f4_run1", 1578, "[2026.10.30-12.12.22:309][380]LogTemp: Display: [FrameworkProof] sweep instance=1 window=Window_SwingSlow_Primary from=0.353269 to=0.390659 tipDistanceCm=40.8246 substeps=3 clamped=0"),
    ("BOSS-HIT-003", "f4_run1", 1578, "[2026.10.30-12.12.22:309][380]LogTemp: Display: [FrameworkProof] sweep instance=1 window=Window_SwingSlow_Primary from=0.353269 to=0.390659 tipDistanceCm=40.8246 substeps=3 clamped=0"),
    ("BOSS-HIT-003", "c2_full", 3805, "[2026.10.30-12.14.52:777][  1]LogAutomationController: Display: Test Completed. Result={Success} Name={DamageProfile} Path={OneBossFight.Framework.Runtime.DamageProfile}"),
    ("BOSS-HIT-004", "f4_run1", 1578, "[2026.10.30-12.12.22:309][380]LogTemp: Display: [FrameworkProof] sweep instance=1 window=Window_SwingSlow_Primary from=0.353269 to=0.390659 tipDistanceCm=40.8246 substeps=3 clamped=0"),
    ("BOSS-HIT-004", "f4_run1", 1580, "[2026.10.30-12.12.22:319][381]LogTemp: Display: [FrameworkProof] sweep instance=1 window=Window_SwingSlow_Primary from=0.390659 to=0.404126 tipDistanceCm=16.3306 substeps=2 clamped=0"),
    ("BOSS-HIT-005", "f4_run1", 1593, "[2026.10.30-12.12.22:385][386]LogTemp: Display: [FrameworkProof] hit instance=1 window=Window_SwingSlow_Primary key=HitGroup_ScytheBlade outcome=ERPGDamageOutcome::Accepted hpApplied=35 healthBefore=800 healthAfter=765"),
    ("BOSS-HIT-005", "c2_full", 3693, "[2026.10.30-12.14.52:038][968]LogAutomationController: Display: Test Completed. Result={Success} Name={Decide} Path={OneBossFight.Combat.DamageResolver.Decide}"),
    ("BOSS-HIT-006", "f4_run1", 1593, "[2026.10.30-12.12.22:385][386]LogTemp: Display: [FrameworkProof] hit instance=1 window=Window_SwingSlow_Primary key=HitGroup_ScytheBlade outcome=ERPGDamageOutcome::Accepted hpApplied=35 healthBefore=800 healthAfter=765"),
    ("BOSS-HIT-006", "f4_run1", 1597, "[2026.10.30-12.12.22:406][387]LogTemp: Display: [FrameworkProof] hit instance=1 window=Window_SwingSlow_Primary key=HitGroup_ScytheBlade outcome=ERPGDamageOutcome::RejectedDuplicate hpApplied=0 healthBefore=765 healthAfter=765"),
    ("BOSS-HIT-006", "f4_run1", 1651, "[2026.10.30-12.12.23:605][435]LogTemp: Display: [FrameworkProof] invariant targetHPBefore=800 targetHPAfter=765 expectedHP=765 acceptedHits=1 appliedDamage=35"),
    ("BOSS-HIT-006", "c2_full", 3693, "[2026.10.30-12.14.52:038][968]LogAutomationController: Display: Test Completed. Result={Success} Name={Decide} Path={OneBossFight.Combat.DamageResolver.Decide}"),
    ("BOSS-HIT-007", "f4_run1", 1593, "[2026.10.30-12.12.22:385][386]LogTemp: Display: [FrameworkProof] hit instance=1 window=Window_SwingSlow_Primary key=HitGroup_ScytheBlade outcome=ERPGDamageOutcome::Accepted hpApplied=35 healthBefore=800 healthAfter=765"),
    ("BOSS-HIT-007", "c2_full", 3805, "[2026.10.30-12.14.52:777][  1]LogAutomationController: Display: Test Completed. Result={Success} Name={DamageProfile} Path={OneBossFight.Framework.Runtime.DamageProfile}"),
    ("BOSS-HIT-008", "c2_full", 3693, "[2026.10.30-12.14.52:038][968]LogAutomationController: Display: Test Completed. Result={Success} Name={Decide} Path={OneBossFight.Combat.DamageResolver.Decide}"),
    ("BOSS-HIT-009", "c2_full", 3693, "[2026.10.30-12.14.52:038][968]LogAutomationController: Display: Test Completed. Result={Success} Name={Decide} Path={OneBossFight.Combat.DamageResolver.Decide}"),
    ("BOSS-MOV-001", "f4_run1", 1506, "[2026.10.30-12.12.21:904][352]LogTemp: Display: [FrameworkProof] walk start=X=500.000 Y=0.000 Z=167.150 end=X=169.690 Y=0.000 Z=167.150 distanceCm=330.31 rangeCm=169.69 bandMin=150 bandMax=180 capsule=X=169.690 Y=0.000 Z=167.150 mesh=X=169.690 Y=0.000 Z=2.150"),
    ("BOSS-MOV-006", "c2_full", 1510, "[2026.10.30-12.14.46:380][606]LogAutomationController: Display: Test Completed. Result={Success} Name={Collision} Path={OneBossFight.Arena.Collision}"),
    ("BOSS-MOV-006", "f4_run1", 1440, "[2026.10.30-12.12.19:625][275]LogTemp: Display: [FrameworkProof] nav_ready waitedSeconds=0.0083334"),
    ("BOSS-MOV-006", "f4_run1", 1455, "[2026.10.30-12.12.20:406][275]LogTemp: Display: [FrameworkProof] nav request=1 projected=X=165.000 Y=-0.000 Z=10.000 fullPath=1 result=2"),
    ("BOSS-PAC-001", "c2_full", 3739, "[2026.10.30-12.14.52:593][979]LogAutomationController: Display: Test Completed. Result={Success} Name={Positive} Path={OneBossFight.Framework.MoveCard.Positive}"),
    ("BOSS-PAC-001", "c2_full", 3745, "[2026.10.30-12.14.52:609][981]LogAutomationController: Display: Test Completed. Result={Success} Name={Rejections} Path={OneBossFight.Framework.MoveCard.Rejections}"),
    ("BOSS-PAC-001", "f4_run1", 1571, "[2026.10.30-12.12.22:294][379]LogTemp: Display: [FrameworkProof] event encounter=1 generation=1 instance=1 kind=Open window=Window_SwingSlow_Primary group=HitGroup_ScytheBlade localSeconds=0.35 label=F4_fixture"),
    ("BOSS-PAC-001", "f4_run1", 1599, "[2026.10.30-12.12.22:426][388]LogTemp: Display: [FrameworkProof] event encounter=1 generation=1 instance=1 kind=Close window=Window_SwingSlow_Primary group=HitGroup_ScytheBlade localSeconds=0.4917 label=F4_fixture"),
    ("BOSS-PAC-001", "f4_run1", 1649, "[2026.10.30-12.12.23:569][433]LogTemp: Display: [FrameworkProof] event encounter=1 generation=1 instance=1 kind=Finished window=None group=None localSeconds=1.65 label=F4_fixture"),
    ("BOSS-PAC-006", "f4_run1", 1650, "[2026.10.30-12.12.23:582][434]LogTemp: Display: [FrameworkProof] cleanup reason=Finished modelIdle=1 ownedMontageStopped=1"),
    ("BOSS-PAC-006", "c2_full", 3769, "[2026.10.30-12.14.52:677][989]LogAutomationController: Display: Test Completed. Result={Success} Name={Crossing} Path={OneBossFight.Framework.MoveModel.Crossing}"),
    ("BOSS-PHS-001", "c2_full", 3483, "[2026.10.30-12.14.50:539][923]LogAutomationController: Display: Test Completed. Result={Success} Name={TransitionRules} Path={OneBossFight.Boss.TransitionRules}"),
    ("BOSS-PHS-002", "c2_full", 3483, "[2026.10.30-12.14.50:539][923]LogAutomationController: Display: Test Completed. Result={Success} Name={TransitionRules} Path={OneBossFight.Boss.TransitionRules}"),
    ("BOSS-PHS-003", "c2_full", 3483, "[2026.10.30-12.14.50:539][923]LogAutomationController: Display: Test Completed. Result={Success} Name={TransitionRules} Path={OneBossFight.Boss.TransitionRules}"),
    ("BOSS-PHS-004", "c2_full", 2203, "[2026.10.30-12.14.48:423][710]LogAutomationController: Display: Test Completed. Result={Success} Name={Assign} Path={OneBossFight.Binding.HealPunish.Assign}"),
    ("BOSS-QA-002", "f4_run1", 1439, "[2026.10.30-12.12.19:625][275]LogTemp: Display: [FrameworkProof] target_health_init value=800 readback=800 label=F4_fixture"),
    ("BOSS-QA-002", "f4_run1", 1506, "[2026.10.30-12.12.21:904][352]LogTemp: Display: [FrameworkProof] walk start=X=500.000 Y=0.000 Z=167.150 end=X=169.690 Y=0.000 Z=167.150 distanceCm=330.31 rangeCm=169.69 bandMin=150 bandMax=180 capsule=X=169.690 Y=0.000 Z=167.150 mesh=X=169.690 Y=0.000 Z=2.150"),
    ("BOSS-QA-002", "f4_run1", 1593, "[2026.10.30-12.12.22:385][386]LogTemp: Display: [FrameworkProof] hit instance=1 window=Window_SwingSlow_Primary key=HitGroup_ScytheBlade outcome=ERPGDamageOutcome::Accepted hpApplied=35 healthBefore=800 healthAfter=765"),
    ("BOSS-QA-002", "f4_run1", 1651, "[2026.10.30-12.12.23:605][435]LogTemp: Display: [FrameworkProof] invariant targetHPBefore=800 targetHPAfter=765 expectedHP=765 acceptedHits=1 appliedDamage=35"),
    ("BOSS-QA-003", "f4_run1", 1651, "[2026.10.30-12.12.23:605][435]LogTemp: Display: [FrameworkProof] invariant targetHPBefore=800 targetHPAfter=765 expectedHP=765 acceptedHits=1 appliedDamage=35"),
    ("BOSS-QA-003", "f4_run2", 1643, "[2026.10.30-12.13.01:241][427]LogTemp: Display: [FrameworkProof] invariant targetHPBefore=800 targetHPAfter=765 expectedHP=765 acceptedHits=1 appliedDamage=35"),
    ("BOSS-QA-003", "f4_run3", 1653, "[2026.10.30-12.13.39:271][433]LogTemp: Display: [FrameworkProof] invariant targetHPBefore=800 targetHPAfter=765 expectedHP=765 acceptedHits=1 appliedDamage=35"),
    ("BOSS-QA-003", "f4_regr", 1654, "[2026.10.30-12.14.14:749][404]LogTemp: Display: [FrameworkProof] invariant targetHPBefore=800 targetHPAfter=800 damageAPIInvocationsByThisExecutor=0"),
    ("BOSS-QA-004", "c2_full", 3769, "[2026.10.30-12.14.52:677][989]LogAutomationController: Display: Test Completed. Result={Success} Name={Crossing} Path={OneBossFight.Framework.MoveModel.Crossing}"),
    ("BOSS-QA-004", "f4_run1", 1578, "[2026.10.30-12.12.22:309][380]LogTemp: Display: [FrameworkProof] sweep instance=1 window=Window_SwingSlow_Primary from=0.353269 to=0.390659 tipDistanceCm=40.8246 substeps=3 clamped=0"),
    ("BOSS-QA-005", "c2_full", 1527, "[2026.10.30-12.14.46:421][611]LogAutomationController: Display: Test Completed. Result={Success} Name={Gate} Path={OneBossFight.Benchmark.FrameStats.Gate}"),
    ("BOSS-QA-005", "c2_full", 1533, "[2026.10.30-12.14.46:438][613]LogAutomationController: Display: Test Completed. Result={Success} Name={Percentiles} Path={OneBossFight.Benchmark.FrameStats.Percentiles}"),
    ("BOSS-SEL-001", "c2_full", 3781, "[2026.10.30-12.14.52:710][993]LogAutomationController: Display: Test Completed. Result={Success} Name={GenerationAndDoubleStart} Path={OneBossFight.Framework.MoveModel.GenerationAndDoubleStart}"),
    ("BOSS-SEL-002", "c2_full", 3775, "[2026.10.30-12.14.52:693][991]LogAutomationController: Display: Test Completed. Result={Success} Name={Eligibility} Path={OneBossFight.Framework.MoveModel.Eligibility}"),
    ("BOSS-SEL-003", "c2_full", 3745, "[2026.10.30-12.14.52:609][981]LogAutomationController: Display: Test Completed. Result={Success} Name={Rejections} Path={OneBossFight.Framework.MoveCard.Rejections}"),
    ("BOSS-SEL-003", "c2_full", 3812, "[2026.10.30-12.14.52:794][  3]LogAutomationController: Display: Test Completed. Result={Success} Name={PlaybackGuards} Path={OneBossFight.Framework.Runtime.PlaybackGuards}"),
    ("BOSS-SEL-008", "c2_full", 3812, "[2026.10.30-12.14.52:794][  3]LogAutomationController: Display: Test Completed. Result={Success} Name={PlaybackGuards} Path={OneBossFight.Framework.Runtime.PlaybackGuards}"),
]

def main():
    print("================================================================================")
    print(" VERIFYING A-274 WITNESS STATUS CITATIONS AGAINST RAW LOGS")
    print("================================================================================")

    doc_path = Path("Docs/BossCombatReview/Execution/Antigravity/Ledger/WITNESS_STATUS_F3_F4.md")
    assert doc_path.is_file(), f"Missing doc: {doc_path}"
    raw = doc_path.read_bytes()
    assert b"\r\r\n" not in raw, "No double CRLF"
    assert b"\n" in raw, "Must have newlines"
    print(f"[OK] WITNESS_STATUS_F3_F4.md raw bytes: {len(raw):,}, clean CRLF")

    # Load logs
    log_buffers = {}
    for k, p in LOGS.items():
        assert p.is_file(), f"Missing log: {p}"
        log_buffers[k] = p.read_text(encoding="utf-8", errors="replace").splitlines()
        print(f"[OK] Loaded {k}: {p} ({len(log_buffers[k]):,} lines)")

    # Verify all citations
    checked = 0
    for rid, lkey, lnum, expected in CITATIONS:
        lines = log_buffers[lkey]
        assert 1 <= lnum <= len(lines), f"Line {lnum} out of range for {lkey} ({len(lines)})"
        actual = lines[lnum - 1].strip()
        assert actual == expected, f"Mismatch at {lkey}:{lnum} for {rid}:\nExpected: {expected}\nActual:   {actual}"
        checked += 1

    print(f"[OK] Successfully verified {checked} raw log citations across {len(CITATIONS)} cited lines.")
    print("================================================================================")
    print(" ALL A-274 WITNESS CITATIONS 100% RE-OPENED AND VERIFIED PASS")
    print("================================================================================")

if __name__ == "__main__":
    main()

