# Validate Boss AnimBlueprint (Queue F-C C2)

For the single-command route, select exactly one supported asset (a boss `AnimBlueprint` or `RPGBossFrameworkProfile`) and run:

```python
exec(open('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/C2/run_validate_boss.py', encoding='utf-8').read())
```

The dispatcher emits a structured selection receipt if the selection is empty, multiple, or unsupported. The direct actions below remain available for focused use.

1. Open the project in the Unreal Editor and select exactly one boss `AnimBlueprint` in the Content Browser.
2. Open the Python Console from the Editor's Output Log panel.
3. Execute:

   ```python
   exec(open('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/C2/validate_selected_anim_blueprint.py', encoding='utf-8').read())
   ```

4. Review the modal summary. The `[C2_VALIDATE]` JSON record in the Editor log contains the asset path, compile status before/after, generated class, and structured diagnostics.

The action refuses zero or multiple selected assets and non-AnimBlueprint assets. It does not need or inspect a loaded map, does not start PIE, and does not save assets. It compiles only the selected AnimBlueprint and then reads its compile status and generated class.

UE 5.5's Python `BlueprintEditorLibrary.compile_blueprint` returns `None`; the script therefore reads the Blueprint status and generated class, and tails newly written `[Compiler]` lines from the project Editor log where available. Compiler messages without an asset name/path are marked as unattributed. This is compile validation only: it does not check the profile's mesh/skeleton pairing, weapon sockets, AnimGraph FullBody slot, move cards, or framework profile domains. Those remain separate preflight requirements.

No Editor run has validated this script in UE 5.5.4 yet. Lead should check the runtime Python API and log destination before treating the action as accepted.

## Profile preflight

To validate a framework profile's reflected values and resolved move-card data without compiling or saving it, select exactly one `URPGBossFrameworkProfile` and run:

```python
exec(open('C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/C2/validate_selected_boss_profile.py', encoding='utf-8').read())
```

The action maps the selected asset into the existing pure `validate_boss_config.py` preflight and returns its blocker tokens with field context. Invalid profiles are refused before any compile call. It does not write or save assets and can be repeated safely. It checks the offline validator's current rules; it is not a direct call to the native `RPGFramework::ValidateProfile`, so rule parity still needs Lead review.
