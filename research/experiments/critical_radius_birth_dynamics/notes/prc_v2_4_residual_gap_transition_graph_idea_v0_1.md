# PRC v2.4 Idea: Residual Gap Transition Graphs

Status: future-work idea, not part of the v2.3 candidate.

The likely v2.4 direction is to extend v2.3 birth dynamics from "the final old
gap closes" to the full exact transition of residual gaps as prime-prefix arcs
are added.

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

Each old open gap should be classified by its transition under the new arc:

```text
miss   : the new arc does not touch the gap
trim   : the new arc cuts off part of the gap
split  : the new arc enters the gap interior and leaves multiple child gaps
close  : the new arc covers the gap
```

In this language, a birth is an extinction event: every old gap is closed by
the new arc. The existing v2.3 `B_5/B_6/B_7` strict single-gap results become
the first finite cases of this transition-graph view.

Likely v2.4 scope:

```text
1. Define exact residual gap nodes and transition edges.
2. Prove/check measure and component transition identities.
3. Reinterpret B_5 as gap extinction using the existing C4/B5 certificates.
4. Promote C5->C6 transition data only if the exact checker path is ready.
5. Treat no-multi-gap / single-gap birth as a lemma candidate, not as an
   overclaimed theorem until verified.
```

Do not add this to v2.3 except as a short future-work pointer. Finish v2.3
first around critical radius, birth containment, strict single-gap finite
evidence, and near-miss/alignment diagnostics.
