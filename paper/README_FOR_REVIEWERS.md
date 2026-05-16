# README for Reviewers

This bundle is a short reading path for the v2.7.1 PRC theorem.  It is meant to
make the mathematical claim easy to inspect without reading the whole research
history.

## Claim

Inside the PRC circular-arc model, for any old residue and any later odd prime
`q>p_k`, a nonempty direct one-prime q-lift occurs exactly when the old residual
set has one gap and the `q`-grid hits its aperture window.

## 30-minute read path

1. Read `paper/primeclock_prc_single_gap_aperture_classification.md`.
2. Check the abstract short-arc obstruction in Section 3.1.
3. Check the PRC component lower bound in Section 3.2.
4. Check the aperture inequality in Section 3.5.
5. Skim `THEOREM_NOTE.md` for the full theorem-note version.
6. Run the finite audit command if you want implementation evidence:

```bash
python3 research/experiments/critical_radius_birth_dynamics/check_v2_7_strict_single_gap_aperture_exact_audit.py
```

## Proof and checks

| Item | Role |
| --- | --- |
| Paper | short exposition of the geometric proof |
| THEOREM_NOTE.md | full theorem-note proof |
| Exact rational sanity check | finite sanity check of definitions and examples |
| Recorded birth rows consistency audit | checks committed CSV birth rows against the next-prime corollary |
| Release integrity checks | distribution, DOI, manifest, and hash verification |

The recorded birth rows consistency audit is not a full finite-universe
completeness audit and not the proof of the theorem.

## Non-claims

This work does not claim:

- no B8 theorem;
- no full transition-graph theorem;
- no general predictor;
- no asymptotic law;
- no prime-gap theorem outside PRC model;
- not a full finite-universe completeness audit;
- no mechanically verified proof.
