# PRC v2.5 Residual Dynamics Seed

This source-only note records the v2.5 shift from final close/birth checks to
residual gap dynamics.

## Model

Each checked lineage is represented by exact rational residual states across
prime-prefix layers.  The canonical row fields are:

```text
scope, lineage_id, layer_k, residue_mod_m, old_component_count,
new_component_count, component_delta, total_residual_measure,
max_component_width, transition_label, phase_margin, capacity_pass,
is_close, is_birth, lineage_role
```

The primary transition labels are kept small:

```text
start, miss, trim, split, partial_close, close
```

Fine structure is stored as attributes rather than new headline labels.

## Lineage Roles

- `close`: checked B5/B6/B7 birth lineages that reach zero residual state.
- `nonclose`: sibling controls in the same birth-parent families that do not
  close.
- `near_miss`: best non-close sibling inside a close-capable family by signed
  phase margin.
- `capacity_nonclose`: capacity-satisfied families that still do not close.

## Boundary

The v2.4 signed phase-margin separator remains important, but v2.5 uses it as
a terminal diagnostic.  The v2.5 research question is whether prior residual
state and transition grammar explain more than width/capacity alone.

## Current Status

This is source-only research material.  It is not a public claim and is not
included in the v2.3 public release bundle.

Initial checked counts:

```text
state transition rows = 369824
final lineages        = 53336
close lineages        = 770
capacity_nonclose     = 40498
near_miss             = 770
nonbirth close        = 0
```

The first ablation is intentionally conservative.  Width-only and simple state
features do not recover checked closes in the top-k diagnostic, while signed
phase margin remains a perfect terminal separator in the checked scopes.  This
means v2.5 should not claim that Residual Dynamics already outperforms the
terminal separator.  The next research question is narrower: whether grammar
and obstruction summaries explain *why* margin-positive lineages arise or fail.

The breakthrough diagnostics add a more aggressive test: prefix-only grammar,
same-family close/near-miss counterfactuals, refined obstruction classes, and
B8 source-only probes.  The first B8 capacity-top probe is negative; the
aperture-orbit recovery probe finds source-only B8 geometry closes in a more
diverse selected panel.  These remain Gate R evidence only, not public claims.
