# UnitGate limitations

- Checks **dimensional consistency only** — a dimensionally valid equation can still be physically wrong; a dimensionally invalid one is definitely wrong. It does not prove physical truth or replace experiment.
- Handles **products, quotients, sums, differences, parentheses**, and integer powers. Terms joined by `+`/`-` must share one dimension — a mismatched sum is DIMENSIONALLY_INVALID with both dimensions named. Mathematical functions (sin, exp, log), non-integer exponents, and unit *conversion* are out of scope (reported, not guessed).
- Symbol table is finite; unknown/ambiguous symbols return `AMBIGUOUS_NEEDS_CLARIFICATION`.
- Single-letter symbols are inherently ambiguous in physics (e.g. `T` time vs temperature); UnitGate picks the common convention and flags the rest. Use word forms (`energy`, `temperature`) when in doubt.
