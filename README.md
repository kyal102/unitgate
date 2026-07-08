<p align="center"><img src="assets/logo.png" alt="UnitGate" width="140"></p>

# UnitGate

[![CI](https://github.com/kyal102/unitgate/actions/workflows/ci.yml/badge.svg)](https://github.com/kyal102/unitgate/actions/workflows/ci.yml) ![python](https://img.shields.io/badge/python-3.9%2B-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![deps](https://img.shields.io/badge/dependencies-stdlib--only-blue)

**Catch broken physics equations before they become confident AI claims.**

```bash
python -m unitgate "E = m * a"
```
```text
E = m * a
  -> DIMENSIONALLY_INVALID
     lhs: E = M*L^2*T^-2
     rhs: m * a = M*L*T^-2
     E has dimension M*L^2*T^-2, but m * a has dimension M*L*T^-2
```

`F = m * a` is valid. `E = m * a` is not. `E = m * c**2` is. UnitGate computes each side's physical dimension with **exact rational exponents** and tells you whether they match.

## Install / run

No dependencies — pure Python standard library.

```bash
python -m unitgate "F = m * a"
python -m unitgate "E = m * c**2"
python -m unitgate --demo
python -m unitgate --json "E = m * a"
```

Exit code is `1` for a dimensionally invalid equation (handy in scripts/CI).

## What it does — and doesn't

> UnitGate checks **dimensional consistency only**. It does not prove physical truth or replace experiment.

It knows the seven SI base dimensions and common derived quantities (force, energy, power, momentum, pressure, charge, voltage, …) and common symbols (`E, F, m, a, v, p, c, P, t, …`). Unknown/ambiguous symbols are reported as `AMBIGUOUS_NEEDS_CLARIFICATION`, never guessed. Expressions support `* / + -`, parentheses, and integer powers — terms in a sum must share one dimension (`E = ½mv² + mgh` passes; `E = mgh + mv` is flagged with both clashing dimensions). Mathematical functions (sin, exp, log) and non-integer exponents remain out of scope.

See [docs/EXAMPLES.md](docs/EXAMPLES.md) and [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## Ecosystem

Part of the public **ClaimGate** verification-tool ecosystem:

- **ClaimGate** — paste claims, see what survives
- **ClaimLint** — catch unsupported README/docs claims
- **UnitGate** — catch broken physics equations *(this repo)*
- **EvidencePack** — seal claim-check receipts
- **ReplayGate** — replay checks and detect drift
- **ClaimStack Demo** — end-to-end public demo

These are public lite tools. The full private engine and advanced mechanics remain private.

**AI proposes. Gates verify. Unsupported claims do not survive.**
