# PRC Theme Scout v0.2 Additional Themes

Objective: find two more research themes that may be even more interesting
than the v0.1 `C0` adjacent anti-persistence theme.

The previous best alternative was:

```text
C0 adjacent anti-persistence after wheel correction.
```

This v0.2 pass found two stronger or at least equally strong themes.

## Theme 1: Small-Prime Wheel Covering Strata

Core observation:

```text
N == 208 mod 210  -> C0(N)=1 for every tested N in 2 <= N <= 10^6
N == 2 mod 210    -> C0(N)=1 for every tested N except N=2
```

Evidence:

```text
residue 208 mod 210: 4761 / 4761 complete, rate 1.000000
residue   2 mod 210: 4761 / 4762 complete, rate 0.999790
```

This is not merely a statistical concentration. For these two residues, the
small primes `2,3,5,7` already cover the circle:

```text
small-prime-covered residues mod 210 = {2, 208}
```

The generated table is:

```text
data/summaries/prc_c0_wheel_residue_rates_2_1000000.csv
```

Why this is more interesting than the previous anti-persistence theme:

- it explains a large part of `C0` directly, not only a transition statistic;
- it separates trivial complete coverage from genuinely nontrivial complete
  coverage;
- it shows that any future `C0` analysis must stratify by small-prime wheel
  classes before making claims;
- it connects PRC to a finite covering-system style question:

```text
which residue classes modulo primorials are already covered by the first few
prime arcs?
```

This also reframes earlier `C0` work. Among the `23571` complete values up to
`10^6`, `9522` are in the two small-prime deterministic classes. The remaining
`14049` are the genuinely nontrivial complete values for later `C0` analysis.

Nontrivial residues still have a strong hierarchy:

```text
top nontrivial residue rates mod 210:
111 -> 854 / 4762 ~= 0.1793
 99 -> 841 / 4762 ~= 0.1766
118 -> 642 / 4762 ~= 0.1348
 88 -> 635 / 4762 ~= 0.1333
122 -> 635 / 4762 ~= 0.1333
```

These classes are not complete from `2,3,5,7` alone, but their small-prime
residual uncovered measure is already small. Excluding the trivial residues,
the correlation between small-prime uncovered measure and complete-covering
rate across mod-210 classes is about:

```text
corr ~= -0.574
```

So the better theme is not just the two deterministic residues. It is a
small-prime residual hierarchy:

```text
small-prime arcs create a wheel-indexed residual landscape, and later primes
only finish some residue classes at high rates.
```

Verdict: **stronger than v0.1**. This is now the first thing to account for
before any `C0` transition or density claim.

## Theme 2: Complete-Covering Cliffs

Core observation:

Selected windows show that complete values are often adjacent to ordinary
uncovered mass. Even after removing the two trivial small-prime residues,
complete coverage is not usually sitting inside a flat almost-covered basin.

Generated table:

```text
data/summaries/prc_selected_window_c0_cliffs_v0_1.csv
```

Evidence from the selected broad `R=250` windows and the original two candidate
windows:

```text
all C0-neighbor cliff rows:
count = 416
median neighbor A(N) ~= 0.0510
max neighbor A(N) ~= 0.1486

nontrivial C0-neighbor cliff rows:
count = 258
median neighbor A(N) ~= 0.0510
max neighbor A(N) ~= 0.1486
```

The two source window sets separately tell the same story:

```text
broad selected windows:
  into C0 previous A median ~= 0.0509
  out of C0 next A median   ~= 0.0542
  nontrivial into median    ~= 0.0497
  nontrivial out median     ~= 0.0554

original candidate windows:
  into C0 previous A median ~= 0.0471
  out of C0 next A median   ~= 0.0446
  nontrivial into median    ~= 0.0508
  nontrivial out median     ~= 0.0417
```

Why this is interesting:

- it asks about local dynamics of `A(N)`, not just exact zero membership;
- it survives after removing the obvious `mod 210` deterministic residues;
- it gives a visual and mechanistic direction:

```text
what changes in the endpoint arrangement when one step takes A(N) from about
0.05 to exactly 0 and then back out again?
```

This theme is distinct from adjacent anti-persistence. Anti-persistence asks
whether `C0(N+1)` happens. Cliff dynamics asks how the uncovered set itself
opens and closes by a large amount over one step.

Verdict: **at least equal to v0.1 as a qualitative research theme**, especially
if paired with endpoint witnesses. It is less theorem-like than Theme 1, but
more geometrically explanatory.

## Ranking After v0.2

Current ranking:

1. **Small-prime wheel covering strata and residual hierarchy.**
2. **Complete-covering cliff dynamics.**
3. `C0` adjacent anti-persistence after wheel correction.
4. PRC residual fragmentation against branch-uniform null.

This ranking is provisional. The main reason Theme 1 moves to the top is that
it changes the interpretation of every `C0` result: a large block of complete
values is already explained by the first four prime arcs.

## Immediate Next Work

For Theme 1:

1. Prove the finite residue statement for `{2,208} mod 210` directly from the
   arcs of `2,3,5,7`.
2. Generate the same table for mod `2310` using primes `2,3,5,7,11`.
3. Recompute all `C0` transition and density summaries after excluding
   small-prime deterministic strata.

For Theme 2:

1. Add endpoint witness rows for nontrivial cliffs.
2. Compare cliff sizes for complete values against matched non-complete local
   minima.
3. Draw one local window figure where `A(N)` repeatedly drops to zero and
   reopens above `0.05`.

## Non-Claims

- Do not treat all `C0` values as equally nontrivial.
- Do not claim the nontrivial residue hierarchy is asymptotic.
- Do not claim selected-window cliffs are globally representative.
- Do not claim the raw selected windows are unbiased samples of all `N`.

## Work Report

Purpose: find two additional themes more interesting than the previous v0.1
theme.

Current attainment: **100% for this scouting request**. Two concrete themes
were found, both tied to generated CSV evidence.

Estimated slices to polished artifacts:

- Theme 1: **2 slices** to become a short rigorous note, because the `{2,208}
  mod 210` small-prime covering statement can likely be proved directly.
- Theme 2: **3 slices** to become a convincing geometric note, because it needs
  endpoint witnesses and matched non-complete comparisons.
