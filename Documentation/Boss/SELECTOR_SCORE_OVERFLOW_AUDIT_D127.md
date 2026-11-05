# Queue D127 — selector score overflow audit

Date: 2026-11-03  
Method: static bound analysis of candidate initialization and score computation; no tests run.

## Source bounds

`FRPGBossMoveSelector::Initialize` requires `Weight` and each of Kite/Hug/BackDodge/Greed multipliers to be finite, strictly positive, and at most `1e6`. `Select` multiplies the weight by `RangeFactor`, `Repeat`, and a product of at most four selected context multipliers, then casts to float. RangeFactor is in `[0.5,1]`; Repeat is either 1 or configured `RepeatPenalty` in `(0,1]`. Config validates RepeatPenalty in `(0,1]`. Since the arithmetic is promoted to double by `RangeFactor`, a conservative positive upper bound is `1e6 * (1e6)^4 = 1e30`, below `float` maximum (~`3.4e38`). Thus accepted initialized candidates cannot produce a non-finite/overflowed score from these factors.

## Zero-score edge

The lower bound is not similarly protected: strictly positive subnormal float weights/multipliers can multiply down below float's representable range and cast to `0.f`. The trace remains `bEligible=true`; if it is the only candidate, the selector can choose that eligible zero-score card. Normal authored weights are unlikely to be subnormal, but source does not set a lower bound beyond `>0`. Existing selector tests cover zero-weight refusal and ordinary score/context cases; they do not cover subnormal products.

## Result / limits

No non-finite score path found under validated candidate/config domains; maximum accepted factors remain below float overflow. There is a distinct underflow-to-zero/eligible-candidate edge, not an overflow finding. Whether to reject subnormal scores or enforce a positive post-cast score is a contract choice. No source change or test run.
