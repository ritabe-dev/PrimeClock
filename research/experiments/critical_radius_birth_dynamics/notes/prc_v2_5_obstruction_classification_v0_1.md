# PRC v2.5 Obstruction Classification Seed

The obstruction classification records why represented lineages do not close.
It is subordinate to Residual Dynamics.

Allowed buckets:

```text
capacity_obstruction
phase_obstruction
multi_component_obstruction
near_miss_obstruction
lineage_obstruction
arithmetic_obstruction
unclassified
```

`unclassified` is intentionally allowed.  The checker should not force every
non-close row into a story if the current diagnostics do not justify it.

The main guard is that close rows must not receive obstruction labels.
