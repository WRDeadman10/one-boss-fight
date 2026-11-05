# E164 decision audit: unreachable combo nodes

The D124/D125 references correctly cover malformed edges and root-reachable path validation. `RPGBossCombo::Validate` requires graph edges to name existing nodes and the graph to be acyclic, but `LongestPath` measures the path from `Root`; valid nodes outside that reachable set do not extend the root path. D125 records that an orphan acyclic node is accepted.

This is an explicit graph contract in source. No new decision is needed if designers may retain unused nodes. If authored unreachable nodes should be rejected as a content-quality rule, owner approval is needed before tightening validation. Lead reviews implementation. Static only; no tests/build/Editor run.
