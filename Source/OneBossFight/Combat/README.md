# Combat utilities

This folder contains small bridges around input injection, animation/skeleton authoring, and test input. It does not own the framework boss attack timeline or damage policy.

## Files

- `RPGInputTestUtils` validates controllers/subsystems/actions/keys, injects Enhanced Input action/key events, and provides a fixed-frame-rate seam for automation (`RPGInputTestUtils.cpp:23-68,95-112`). It is for development/test drivers; Shipping implementations fail closed or are compiled out as guarded (`:14-20,55-68,95-112`).
- `RPGMontageUtils` describes montage sections/notifies and editor-side montage helpers (`RPGMontageUtils.cpp:8-49`).
- `RPGSkeletonUtils` copies/inspects sockets with editor guards and validates source/target bones (`RPGSkeletonUtils.cpp:10-58`).

## Use and limits

PIE drivers should inject real mapped actions through the helper instead of calling private input-buffer APIs. Do not edit components with `set_editor_property` during PIE: construction reruns can break gameplay effects. Skeleton socket writes are editor authoring operations, not runtime combat behavior. For attack timing and damage flow, see `Documentation/Boss/DATA_FLOW_ATTACK.md`.
