# Claude-only verification commands

These are instructions, not Codex execution results. Recheck current promotion state: live source changed concurrently after X147 delivery; do NOT apply the patch a second time. Preimage hashes in JSON describe original delivery only.

After reviewing promoted diff and closing editor, from project root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/Rebuild.ps1 -Tests
& 'C:/Program Files/Epic Games/UE_5.5/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' 'C:/UnrealProject/OneBossFight/OneBossFight.uproject' '-ExecCmds=Automation RunTests OneBossFight.Catalog.Resolution; Quit' -unattended -nullrhi -nosound -nosplash
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/RunDrivers.ps1
```

Record actual logs/results; watch for TESTS DID NOT RUN, do not accept exit0 alone. Use established project cook/stage procedure for a fresh cold Development package; this delivery deliberately does not invent packaging options or execute another editor chain.

Native API spot checks against installed UE5.5: Field.h GetOwnerStruct declaration line657; UnrealType.h FObjectPropertyBase getters/setter line2651–2658. Reflection helper uses native FClassProperty/FObjectProperty/FArrayProperty/FStructProperty and FScriptArrayHelper rather than parsing exported values. These spot checks do NOT replace compilation and complete adapter API review by Claude.
