# PRC Fast Scan v0.2

This note records the first scanner upgrade for extending PRC consecutive-run
experiments beyond `N=10^6`.

## Goal

The v0.1 scanner can certify complete-covering values, but the pure Python
numeric prefilter is too slow for broad `N>10^6` scans.

The v0.2 goal is narrower:

```text
build a practical scanner foundation for N <= 10^7
run benchmark windows
run one pilot range: 1,000,001 <= N <= 1,100,000
do not claim a full N <= 10^7 scan yet
```

## Engine

`covering-run-prefilter-scan` now supports:

```bash
--engine python
--engine numpy
```

The `numpy` engine keeps the same logic:

```text
numeric prefilter -> exact rational certification for numeric candidates
```

Only the numeric prefilter is vectorized. Every reported `C0(N)=1` value is
still certified by exact rational interval arithmetic.

## Guardrail

The documented prefilter guardrail is extended to:

```text
PREFILTER_GUARANTEE_MAX_N = 10,000,000
DEFAULT_PREFILTER_TOLERANCE = 1e-12
required_prefilter_tolerance = 4096 * eps ~= 9.09e-13
```

For `N <= 10^7`,

```text
2*(N mod p)+1 <= 2*10^7+1 << 2^53
```

so the integer quantities used before endpoint division are exactly
representable in binary64. The note remains implementation-scoped: this is a
guardrail for the scanner, not a theorem about PRC.

## Benchmark

Generated with these commands:

```bash
python -m prime_reciprocal_projection.cli covering-run-benchmark \
  --window 1000001 1001000 n1m_1000 \
  --engine python numpy \
  --chunk-size 1000 \
  --out data/summaries/prc_fastscan_benchmark.csv

python -m prime_reciprocal_projection.cli covering-run-benchmark \
  --window 5000000 5000999 n5m_1000 \
  --engine numpy \
  --chunk-size 1000 \
  --out data/summaries/prc_fastscan_benchmark.csv \
  --append

python -m prime_reciprocal_projection.cli covering-run-benchmark \
  --window 9900000 9900999 n9_9m_1000 \
  --engine numpy \
  --chunk-size 1000 \
  --out data/summaries/prc_fastscan_benchmark.csv \
  --append
```

The `n1m_1000` window is the local Python-vs-NumPy comparison. The `5e6` and
`9.9e6` windows are NumPy-only throughput probes.

Current result:

```text
n1m_1000:
  python: 18.42s, 54.29 N/s
  numpy:   3.51s, 285.25 N/s
  speedup: about 5.3x

n5m_1000:
  numpy: 16.02s, 62.42 N/s

n9_9m_1000:
  numpy: 30.70s, 32.57 N/s
```

The local 5x acceptance threshold is met on `n1m_1000`, but throughput still
drops as `N` grows. A full `10^7` scan should not be launched casually from
this baseline.

## Pilot

Generated with:

```bash
python -m prime_reciprocal_projection.cli covering-run-block-scan \
  --start 1000001 \
  --stop 1100000 \
  --block-size 10000 \
  --workers 4 \
  --chunk-size 1000 \
  --engine numpy \
  --out-dir data/summaries/prc_fastscan_pilot_blocks_1000001_1100000 \
  --combined-out data/summaries/prc_fastscan_pilot_runs_1000001_1100000.csv \
  --summary-out data/summaries/prc_fastscan_pilot_summary_1000001_1100000.csv
```

The sandboxed run hit a macOS `ProcessPoolExecutor` semaphore permission
boundary, so the same command was run outside the sandbox.

Result:

```text
range: 1,000,001 <= N <= 1,100,000
checked values: 100,000
exact-certified complete-covering values: 2,380
runs: 2,378
longest run length: 2
length-2 runs: 2
length-3 starts: 0
```

The two length-2 runs are:

```text
1,035,932, 1,035,933
1,041,927, 1,041,928
```

This is consistent with the v0.1 pattern: exact complete coverage is common
enough to appear around `2.38%` of the time, but adjacent persistence remains
rare.

## Next

Before a full `N <= 10^7` scan, the scanner needs either:

- a stronger algorithmic prefilter that avoids sorting all prime arcs for every
  `N`, or
- a careful long-running block schedule with checkpointing and expected runtime
  recorded upfront.
