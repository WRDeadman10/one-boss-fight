"""Reproduce two synthetic candidate-mode limits; never edits live source or saved evidence.

Exit 0 means the historically pinned helper reproduced both narrow false accepts,
NOT that either candidate is equivalent, safe, compiled, or accepted for integration.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PINS = {
    'Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp':
        '1b036b03aec269e5b3e906d8adaedac709c33f6a3c15413d0454b9c354523712',
    'Docs/BossCombatReview/Execution/Codex/Step2Preparation/legacy_attach_witness.mjs':
        '995376c1f0ca8a2c81a4d6032a1cf00f8df730bd883f2ea48b66afab7e42fe01',
    'Docs/BossCombatReview/Execution/Codex/Step2Preparation/LEGACY_ATTACH_BASELINE_2026-10-26.json':
        '02a72c7a2aaa1c076c9e6ed8a6bfb9dae705304847d031bffbf3bc1bedfe9d51',
}


def main():
    raw = {}
    for relative, expected in PINS.items():
        data = (ROOT / relative).read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected:
            raise RuntimeError('input drift; historical probe refused: ' + relative)
        raw[relative] = data
    node = shutil.which('node')
    if not node:
        raise RuntimeError('Node.js unavailable; probes not run')
    source = raw[next(iter(PINS))].decode('utf-8').replace('\r\n', '\n')
    baseline = json.loads(raw[next(reversed(PINS))])
    changes = [
        ('changed_music_default', 'MX_Boss01_Phase1.MX_Boss01_Phase1',
         'AG17_FakeMusic.AG17_FakeMusic'),
        ('duplicate_spawn_attach', 'Attach(Actor);', 'Attach(Actor); Attach(Actor);'),
    ]
    results = []
    with tempfile.TemporaryDirectory(prefix='ag17_probe_', dir=HERE) as directory:
        target = Path(directory).resolve()
        if not target.is_relative_to(HERE):
            raise RuntimeError('temporary path escaped Codex preparation directory')
        for name, original, replacement in changes:
            if source.count(original) != 1:
                raise RuntimeError('mutation preimage not unique: ' + name)
            candidate = target / (name + '.cpp')
            candidate.write_text(source.replace(original, replacement, 1), encoding='utf-8')
            run = subprocess.run(
                [node, str(HERE / 'legacy_attach_witness.mjs'), '--candidate', str(candidate)],
                capture_output=True, text=True, timeout=30,
            )
            report = json.loads(run.stdout)
            if run.returncode != 0 or report['orderMatches'] is not True:
                raise RuntimeError('historical acceptance outcome changed: ' + name)
            if name == 'changed_music_default':
                if report['bodyTokenSHA256'] == baseline['bodyTokenSHA256']:
                    raise RuntimeError('expected changed body fingerprint not observed')
            elif report['triggerTokensUnchanged'] is not False:
                raise RuntimeError('expected changed trigger fingerprint not observed')
            results.append({
                'case': name,
                'candidate_sha256': hashlib.sha256(candidate.read_bytes()).hexdigest(),
                'helper_exit_code': run.returncode,
                'order_matches': report['orderMatches'],
                'body_token_sha256': report['bodyTokenSHA256'],
                'trigger_tokens_unchanged': report['triggerTokensUnchanged'],
            })
    print(json.dumps({
        'scope': 'Two offline historical false accepts reproduced; not UE or candidate acceptance',
        'input_pins': PINS,
        'results': results,
        'saved_evidence_overwritten': False,
    }, indent=2))


if __name__ == '__main__':
    main()
