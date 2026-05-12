# PRC v2.4 Idea: Residual Gap Transition Graphs

Status: source-only bridge.
Release eligibility: excluded from v2.3 public/candidate bundles and not
promoted as a v2.4 public release.

The v2.4 bridge direction extends the v2.3 gap-aperture birth view from
"which `q`-grid centers close the final old gap?" to the full exact transition
of residual gaps as prime-prefix arcs are added.

The first source-only seed for this direction is:

```text
data/prc_v2_4_b5_gap_close_transition_pilot_v0_1.csv
notes/prc_v2_4_b5_transition_pilot_v0_1.md
```

Those files are v2.4 research material only. They are not part of the v2.3.0
public release or v2.3 candidate package.

Working title:

```text
Exact residual-gap transition graphs for prime-prefix PRC
```

Core object:

```text
R_{k+1}(r') = R_k(r) \setminus J_q(a)
```

where `r'` is a lift of parent `r mod M_k`, `q=p_{k+1}`, `a=r' mod q`, and
`J_q(a)` is the new closed `q`-arc.

The primary v2.4 classification is row-level, not per-gap:

```text
miss          : the new arc does not touch residual set
trim          : the new arc touches residual set, no component vanishes,
                and component count does not increase
split         : the new arc touches residual set, no component vanishes,
                and component count increases
partial_close : at least one component vanishes, but residual set remains
close         : residual set becomes empty
```

Finer shape changes are still carried as attributes, but `split` stays a
primary label because an increased residual component count is qualitatively
different from component-preserving trimming.

In this language, v2.3 gap-aperture births are the `close` geometry case when
that close row is also a first-coverage event. `close` is a geometric residual
extinction state; `birth` is a history label. The existing v2.3 `B_5/B_6/B_7`
unique strict single-gap results become the first finite cases of this
transition-graph view.

v2.4 bridge scope:

```text
1. Define exact residual gap nodes and transition edges.
2. Prove/check measure and component transition identities.
3. Reinterpret B_5 as gap extinction using the existing C4/B5 certificates.
4. Promote C5->C6 transition data only if the exact checker path is ready.
5. Treat no-multi-gap / single-gap birth as a lemma candidate, not as an
   overclaimed theorem until verified.
```

Do not add this to v2.3 except as a short future-work pointer. If this line
feeds a later candidate, recompute and restate the useful diagnostics under the
next version line rather than citing v2.4 as a public result.
