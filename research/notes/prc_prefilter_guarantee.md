# PRC Prefilter Guarantee

This note documents the v0.2 guarantee for the numeric prefilter used in
consecutive-run scans.

The prefilter is not the proof step. It is a fast rejection step:

```text
binary64 numeric coverage check -> exact rational coverage check for candidates
```

False positives are acceptable because every reported value is exact-checked
after the prefilter. The risk to control is false negatives: an exactly
complete-covered `N` that the numeric prefilter rejects.

## Scope

The implemented guarantee is deliberately narrow:

```text
range:        2 <= N <= 10,000,000
arithmetic:   IEEE-754 binary64 floats
tolerance:    1e-12
implementation:
  prime_reciprocal_projection.covering_runs._is_completely_covered_numeric_with_primes
  prime_reciprocal_projection.covering_runs._is_completely_covered_numeric_numpy_with_primes
```

For this range, the CLI refuses guaranteed prefilter scans if the requested
`--stop` exceeds `10,000,000`, unless the user explicitly passes:

```bash
--allow-unguaranteed-prefilter
```

That option is for exploration only. It does not extend the guarantee.

## Endpoint Bound

For each prime `p <= N`, the exact PRC arc endpoints can be written as:

```text
start = (2*(N mod p) - 1) / (2p)
end   = (2*(N mod p) + 1) / (2p)
```

after circular wrap splitting when needed.

Each exact endpoint lies in `[0,1]`. Both prefilter engines compute these
endpoints as binary64 floats from the same numerator/denominator formula:

```text
python engine: scalar float arithmetic over a Python prime list
numpy engine:  vectorized int64 residues followed by float64 division
```

The code uses the conservative bound:

```text
required tolerance = 4096 * eps
```

where `eps = 2^-52 ~= 2.22e-16`, so:

```text
4096 * eps ~= 9.09e-13 < 1e-12
```

This is intentionally much larger than the sharp endpoint rounding error. The
extra slack covers the simple arithmetic path, the NumPy vectorized endpoint
path, adjacent endpoint comparisons, and the merge tolerance used by the scan.

For `N <= 10^7`, the integer numerator quantities also remain far below the
binary64 exact-integer range:

```text
2*(N mod p)+1 <= 2*10^7+1 << 2^53
```

So the v0.2 extension does not introduce a new integer-representation risk
before endpoint division.

## Why This Prevents False Negatives

If the exact circular union covers the full circle, then in the sorted endpoint
merge there is no true positive gap between consecutive covered pieces. Any
gap seen only by the numeric prefilter must therefore be created by floating
endpoint perturbation.

With the default guardrail, the numeric merge tolerance is larger than the
conservative endpoint perturbation budget. Therefore a true exact contact or
overlap cannot become a numeric rejection solely because two endpoints were
rounded apart.

This does not make a floating-point `C0(N)` value a mathematical proof. It only
means the prefilter should not discard exact complete-covering values in the
documented range. Candidate acceptance is still followed by exact rational
interval checking.

## Code Guardrails

The implementation exposes:

```text
DEFAULT_PREFILTER_TOLERANCE = 1e-12
PREFILTER_GUARANTEE_MAX_N = 10_000_000
required_prefilter_tolerance(max_n)
validate_prefilter_tolerance(max_n, tolerance=...)
```

The guarded scanner calls `validate_prefilter_tolerance(stop, ...)` before
running. It raises if:

- `stop > 10_000_000` and guarantee mode is enabled.
- `tolerance < required_prefilter_tolerance(stop)`.

The block/resume scanner applies the same guardrail to resumed block summaries.
It rejects stale block metadata if the stored range, checked count, engine, or
prefilter tolerance does not match the requested scan.

## Claim Status

Safe claim:

```text
For N <= 10^7, the default v0.2 prefilter tolerance is larger than the documented
binary64 endpoint-error guardrail, so the prefilter is intended to be
no-false-negative within this implemented model; all accepted values are still
exact-certified.
```

Non-claims:

- This is not a theorem about PRC itself.
- This does not prove anything for `N > 10^7`.
- This does not replace exact rational certification.
- This does not certify arbitrary Python, platform, or compiler changes unless
  the endpoint computation remains the same binary64 path.
