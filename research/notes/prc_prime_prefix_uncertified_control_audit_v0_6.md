# PRC Prime-Prefix Uncertified Control Audit v0.6

## Purpose

v0.5 showed that nearest distance to the checked `C_8` set is not a
complete-specific explanation: local non-complete controls have nearly the same
distance distribution. v0.6 keeps the same matched profile and asks a narrower
diagnostic question:

```text
Which modulo-210 classes and nearest C_k source depths drive the remaining
complete/control differences?
```

This is still a diagnostic artifact. It does not claim that nearest-`C_8`
distance explains complete covering.

## Inputs

```text
data/summaries/prc_prime_prefix_uncertified_control_profile_v0_5.csv
```

This profile contains:

- `4,495` `complete_uncertified` rows.
- `4,475` `local_mod210_control` rows.
- `4,495` `local_any_control` rows.
- `13,465` rows total.

## Command

```bash
cd research
python -m prime_reciprocal_projection.cli covering-prime-prefix-uncertified-control-audit \
  --profile data/summaries/prc_prime_prefix_uncertified_control_profile_v0_5.csv \
  --mod210-out data/summaries/prc_prime_prefix_uncertified_control_mod210_audit_v0_6.csv \
  --source-depth-out data/summaries/prc_prime_prefix_uncertified_source_depth_summary_v0_6.csv
```

## Outputs

```text
data/summaries/prc_prime_prefix_uncertified_control_mod210_audit_v0_6.csv
data/summaries/prc_prime_prefix_uncertified_source_depth_summary_v0_6.csv
```

The modulo-210 audit has one row per `(control_role, seed_mod210)` class. It
keeps paired counts, median complete/control distances, median paired delta, and
direction counts.

The source-depth summary groups rows by the `C_k` layer that first certifies
the nearest covered residue.

## First Reading

The audit generated `196` modulo-210 rows and `15` source-depth rows.

At the aggregate level, v0.5 remains the right interpretation:

| comparison | complete smaller | complete larger | ties |
|---|---:|---:|---:|
| `local_mod210_control` | 1,654 | 1,511 | 1,310 |
| `local_any_control` | 2,201 | 2,273 | 21 |

So the hard modulo-210 control remains close to the complete rows, and
`local_any_control` is directionally mixed.

The source-depth split is also very similar across roles:

| role | source k=4 | source k=5 | source k=6 | source k=7 | source k=8 |
|---|---:|---:|---:|---:|---:|
| `complete_uncertified` | 1,989 | 1,686 | 386 | 291 | 143 |
| `local_mod210_control` | 2,070 | 1,587 | 305 | 367 | 146 |
| `local_any_control` | 1,989 | 1,684 | 389 | 290 | 143 |

The main new information is class-level, not global. For example, large
modulo-210 classes such as `111`, `4`, `99`, `206`, and `118` have different
paired directions depending on the control type. That is useful for deciding
where to inspect next, but it is not a complete-covering explanation.

## Interpretation

v0.6 strengthens the negative result from v0.5:

```text
nearest distance to C_8 is mainly a local/wheel diagnostic, not a standalone
complete-covering classifier.
```

The next useful step is not to claim significance from these rows. It is to
choose a stricter finite-residue null or inspect a small number of large
modulo-210 classes by hand, especially where paired direction differs between
`local_mod210_control` and `local_any_control`.

## Non-Claims

- This does not prove that `C_8` proximity is irrelevant.
- This does not prove that complete covering is explained by a modulo-210
  class effect.
- This does not justify jumping to `k=9`; the v0.6 artifact is a diagnostic
  split of the existing v0.5 profile.
