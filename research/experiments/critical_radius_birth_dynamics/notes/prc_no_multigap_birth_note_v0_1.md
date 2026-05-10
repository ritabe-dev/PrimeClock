# PRC No Multi-Gap Birth Note v0.1

Status: internal mechanism note / lemma candidate.

In the prime-prefix PRC process, a later birth arc is always shorter than any
earlier arc that could have split one old gap into two gaps. If two old gaps are
separated by an existing `p`-arc, then any later new prime `q` satisfies `q > p`,
so the new arc length is `1/q < 1/p`.

Therefore a later `q`-arc cannot cover both old gaps across the separating
`p`-arc. This explains why the checked layers

```text
B_5, B_6, B_7
```

are all `strict_single_gap_birth`: in this mechanism, births should be expected
to close one old gap, not multiple old gaps at once.

This note is not yet stated as a fully general theorem; it records the current
geometric reason to treat multi-gap birth as structurally suppressed in the
prime-prefix model.
