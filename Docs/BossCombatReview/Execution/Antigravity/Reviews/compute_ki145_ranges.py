#!/usr/bin/env python3
"""
compute_ki145_ranges.py - Recomputes Move Card Geometric & Physical Contact Ranges
Addresses KI-145: Card ranges exceeding measured reach and lateral offset clipping.
Authority: REACH_TO_RANGE_RULES.md, Lead Order [C-461]

Evaluates all 10 existing move cards across F5, F7, and Phase 2 sets:
- Inputs:
    reach_summary.json (all 4 sequences: Swing1_Slow, Swing2_Medium, Swing3_Slow, Swing1_FAST_v2)
    R_target = 42.0 cm (Pack player capsule radius)
    R_boss = 60.0 cm (Boss capsule radius in RPGBossFrameworkProfile fixture)
    BakedSamples from card JSONs
- Computes:
    Segment-to-point Euclidean distance in 2D component plane (+Y forward, X lateral)
    Geometric contact interval [GeomMinCm, GeomMaxCm]
    Physical non-penetration clamped interval [PhysMinCm, PhysMaxCm] (floor = R_boss + R_target = 102.0 cm)
    Proposed calibrated [PropMinCm, PropMaxCm] with outer safety margin (5 cm) and inner physical clearance (5 cm)
    Dead zones where authored range allows selection but weapon cannot hit a centered target
    Predictions at D in {100, 130, 160, 167} cm for PIE verification
"""

import json
import math
import os
import sys
from typing import Dict, List, Any, Tuple, Optional

# Core Physical Dimensions (cm)
R_TARGET = 42.0       # Pack player capsule radius (Claude/F5, KI-145)
R_BOSS = 60.0         # Boss capsule radius (RPGBossFrameworkProfile fixture)
PHYS_MIN_D = R_BOSS + R_TARGET  # 102.0 cm: physical non-penetration floor
SAFETY_OUTER = 5.0    # cm margin to ensure swept volume penetrates target
SAFETY_INNER = 5.0    # cm margin inside physical clearance (102.0 + 5.0 = 107.0 cm -> recommended 105.0 cm)


def dist_point_to_segment_2d(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    """Computes minimum 2D Euclidean distance from point (px, py) to line segment (ax, ay)-(bx, by)."""
    dx = bx - ax
    dy = by - ay
    l2 = dx * dx + dy * dy
    if l2 == 0.0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
    proj_x = ax + t * dx
    proj_y = ay + t * dy
    return math.hypot(px - proj_x, py - proj_y)


def find_dense_samples(baked_samples: List[Dict[str, Any]], num_substeps: int = 10) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
    """Interpolates between consecutive discrete samples to simulate continuous sweep."""
    dense = []
    if not baked_samples:
        return dense
    for i in range(len(baked_samples) - 1):
        s0 = baked_samples[i]
        s1 = baked_samples[i + 1]
        for step in range(num_substeps):
            alpha = step / float(num_substeps)
            bx = s0['BaseCS'][0] * (1.0 - alpha) + s1['BaseCS'][0] * alpha
            by = s0['BaseCS'][1] * (1.0 - alpha) + s1['BaseCS'][1] * alpha
            tx = s0['TipCS'][0] * (1.0 - alpha) + s1['TipCS'][0] * alpha
            ty = s0['TipCS'][1] * (1.0 - alpha) + s1['TipCS'][1] * alpha
            dense.append(((bx, by), (tx, ty)))
    dense.append(((baked_samples[-1]['BaseCS'][0], baked_samples[-1]['BaseCS'][1]),
                  (baked_samples[-1]['TipCS'][0], baked_samples[-1]['TipCS'][1])))
    return dense


def evaluate_card_reach(card: Dict[str, Any], baked_samples_map: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Evaluates geometric and physical contact bounds for a single move card."""
    move_id = card['MoveId']
    seq = card['Sequence'].split('/')[-1].split('.')[0]
    win = card['Windows'][0]
    radius_blade = win.get('RadiusCm', 15.0)
    thresh = radius_blade + R_TARGET
    
    # Get samples either from window or mapped by sequence
    samples = win.get('BakedSamples')
    if not samples:
        samples = baked_samples_map.get(seq, [])
    
    dense_samples = find_dense_samples(samples, num_substeps=10)
    
    # Dense scan from 10.0 to 300.0 cm in steps of 0.5 cm
    hits = []
    for d_int in range(100, 3001, 5):
        d = d_int / 10.0
        min_d = min(dist_point_to_segment_2d(0.0, d, b[0], b[1], t[0], t[1]) for (b, t) in dense_samples)
        if min_d <= thresh:
            hits.append(d)
            
    geom_min = min(hits) if hits else None
    geom_max = max(hits) if hits else None
    
    # Physical contact range: clamped to physical floor R_boss + R_target
    phys_min = max(PHYS_MIN_D, geom_min) if geom_min else None
    phys_max = geom_max
    
    # Calibrated proposed range
    auth_min = card.get('MinRangeCm')
    auth_max = card.get('MaxRangeCm')
    
    # Determine viable proposed range
    if phys_max is not None and phys_max >= PHYS_MIN_D:
        prop_min = 105.0
        prop_max_raw = phys_max - SAFETY_OUTER
        prop_max = math.floor(prop_max_raw / 5.0) * 5.0
        if prop_max < prop_min:
            # If safety margin exceeds physical window, indicate narrow physical window
            is_narrow_window = True
            prop_range_str = f"[{PHYS_MIN_D:.0f}, {phys_max:.0f}] (Narrow: {phys_max - PHYS_MIN_D:.1f}cm window)"
        else:
            is_narrow_window = False
            prop_range_str = f"[{prop_min:.0f}, {prop_max:.0f}]"
    else:
        is_narrow_window = True
        prop_range_str = "UNVIABLE"
        prop_min = None
        prop_max = None
        
    # Flag dead zones
    dead_zones = []
    if auth_max and geom_max and auth_max > geom_max:
        dead_zones.append(f"Upper dead zone [{geom_max + 0.1:.1f}, {auth_max:.1f}] cm (whiff on centered target)")
    if auth_min and auth_min < PHYS_MIN_D:
        dead_zones.append(f"Sub-physical floor [{auth_min:.1f}, {PHYS_MIN_D:.1f}] cm (capsule interpenetration)")
        
    # PIE predictions at key probe distances
    pie_probes = {}
    for d_probe in [100.0, 130.0, 160.0, 167.0]:
        min_dist = min(dist_point_to_segment_2d(0.0, d_probe, b[0], b[1], t[0], t[1]) for (b, t) in dense_samples)
        is_hit = (min_dist <= thresh)
        margin = thresh - min_dist
        pie_probes[d_probe] = {
            'min_dist_cm': round(min_dist, 2),
            'threshold_cm': thresh,
            'margin_cm': round(margin, 2),
            'hit': is_hit
        }
        
    return {
        'MoveId': move_id,
        'Sequence': seq,
        'RadiusBladeCm': radius_blade,
        'ThresholdCm': thresh,
        'AuthMinCm': auth_min,
        'AuthMaxCm': auth_max,
        'GeomMinCm': geom_min,
        'GeomMaxCm': geom_max,
        'PhysMinCm': phys_min,
        'PhysMaxCm': phys_max,
        'PropMinCm': prop_min,
        'PropMaxCm': prop_max,
        'PropRangeStr': prop_range_str,
        'DeadZones': dead_zones,
        'PieProbes': pie_probes
    }


def find_project_root() -> str:
    """Finds project root containing OneBossFight.uproject."""
    curr = os.path.abspath(__file__)
    for _ in range(10):
        curr = os.path.dirname(curr)
        if os.path.exists(os.path.join(curr, 'OneBossFight.uproject')):
            return curr
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))


def run_ki145_evaluation(project_root: Optional[str] = None) -> List[Dict[str, Any]]:
    """Loads all cards and reach data, returning evaluation dictionaries for all 10 cards."""
    if project_root is None:
        project_root = find_project_root()

    f5_path = os.path.join(project_root, 'Docs', 'BossCombatReview', 'Execution', 'Antigravity', 'MoveCards', 'move_cards_f5_set.json')
    f7_path = os.path.join(project_root, 'Docs', 'BossCombatReview', 'Execution', 'Claude', 'F7', 'move_cards_f7_baked.json')
    p2_path = os.path.join(project_root, 'Docs', 'BossCombatReview', 'Execution', 'Antigravity', 'MoveCards', 'move_cards_f7_phase2_set.json')

    with open(f7_path, 'r', encoding='utf-8') as f:
        f7_data = json.load(f)
    with open(f5_path, 'r', encoding='utf-8') as f:
        f5_data = json.load(f)
    with open(p2_path, 'r', encoding='utf-8') as f:
        p2_data = json.load(f)
        
    # Map baked samples by sequence name from F7
    baked_map = {}
    for c in f7_data['cards']:
        seq = c['Sequence'].split('/')[-1].split('.')[0]
        baked_map[seq] = c['Windows'][0]['BakedSamples']
        
    all_cards = []
    # 4 from F5, 4 from F7, 2 from P2
    for c in f5_data['cards']:
        all_cards.append(('F5', c))
    for c in f7_data['cards']:
        all_cards.append(('F7', c))
    for c in p2_data['cards']:
        all_cards.append(('Phase2', c))
        
    results = []
    for set_label, c in all_cards:
        res = evaluate_card_reach(c, baked_map)
        res['Set'] = set_label
        results.append(res)
        
    return results


def main():
    results = run_ki145_evaluation()
    
    if '--json' in sys.argv:
        print(json.dumps(results, indent=2))
        return

    print("=" * 116)
    print(f"{'MoveId':<32} | {'Set':<7} | {'Authored':<12} | {'Geom Range':<15} | {'Phys Hit':<15} | {'Proposed':<20}")
    print("=" * 116)
    for r in results:
        auth = f"[{r['AuthMinCm']:.0f}, {r['AuthMaxCm']:.0f}]"
        geom = f"[{r['GeomMinCm']:.1f}, {r['GeomMaxCm']:.1f}]"
        phys = f"[{r['PhysMinCm']:.1f}, {r['PhysMaxCm']:.1f}]"
        prop = r['PropRangeStr']
        print(f"{r['MoveId']:<32} | {r['Set']:<7} | {auth:<12} | {geom:<15} | {phys:<15} | {prop:<20}")
    print("=" * 116)
    
    print("\n" + "=" * 92)
    print("DEAD ZONE SUMMARY PER MOVE CARD")
    print("=" * 92)
    for r in results:
        print(f"* {r['MoveId']} ({r['Set']}):")
        if r['DeadZones']:
            for dz in r['DeadZones']:
                print(f"    - {dz}")
        else:
            print("    - None (authored range is within contact limits)")

    print("\n" + "=" * 92)
    print("PIE PREDICTION MATRIX AT KEY PROBE DISTANCES (Centered Target X=0)")
    print("=" * 92)
    # Print distinct 4 animations
    seen_seqs = set()
    for r in results:
        if r['Sequence'] in seen_seqs:
            continue
        seen_seqs.add(r['Sequence'])
        print(f"\nSequence: {r['Sequence']} (MoveId: {r['MoveId']}, Blade Radius: {r['RadiusBladeCm']} cm, Threshold: {r['ThresholdCm']} cm)")
        for d, probe in r['PieProbes'].items():
            hit_str = "HIT " if probe['hit'] else "MISS"
            print(f"  Distance {d:5.1f} cm: MinDist = {probe['min_dist_cm']:5.2f} cm (Margin {probe['margin_cm']:+6.2f} cm) -> {hit_str}")


if __name__ == '__main__':
    main()
