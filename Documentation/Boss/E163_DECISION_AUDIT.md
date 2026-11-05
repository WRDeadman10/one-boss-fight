# E163 decision audit: damage-scaler nonfinite policy

The cited D92 audit maps reciprocal damage-scaler boundaries and invalid/nonfinite behavior. Invalid or nonfinite samples are rejected without consuming a pending scaler loss; finite matched reciprocal samples consume the matching loss once. Existing D92 coverage describes exact edges and remaining direct nonfinite fixture gaps.

No new owner policy is needed for the current fail-closed pure-rule behavior. Any change to how invalid data consumes pending state requires owner approval because it changes damage attribution. Lead owns source/test review. Static inspection only; no tests/build/Editor run.
