# PRC v2.3 Standalone Checker TODO

Status: internal public-release blocker.

The current v2.3 checker is an internal helper-based checker. It imports the
experiment helper code, regenerates the candidate rows, and compares them with
the committed CSV artifacts.

Before promoting v2.3 to a public release, add a standalone checker or explicit waiver in the release notes.

## Minimum Standalone Checker

The standalone checker should:

- use only the Python standard library;
- read the committed v2.3 CSV artifacts;
- verify row counts and SHA256 coverage for the candidate CSV set;
- verify the `C_4` and `C_5` critical-radius level-set claims from the CSV rows;
- verify that `B_5`, `B_6`, and `B_7` summary rows are strict single-gap births;
- fail nonzero on missing rows, duplicate rows, wrong status fields, or hash
  mismatches.

This requirement is separate from the existing v2.2.3 standalone checker, which
continues to cover only the stable `C_4/B_5` public certificate package.
