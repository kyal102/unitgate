# UnitGate limitations

- Checks **dimensional consistency only** — a dimensionally valid equation can still be physically wrong; a dimensionally invalid one is definitely wrong. It does not prove physical truth or replace experiment.
- Handles **products and quotients** of symbols with integer powers. Sums, parentheses, and full algebra are out of scope (reported, not guessed).
- Symbol table is finite; unknown/ambiguous symbols return `AMBIGUOUS_NEEDS_CLARIFICATION`.
- Single-letter symbols are inherently ambiguous in physics (e.g. `T` time vs temperature); UnitGate picks the common convention and flags the rest. Use word forms (`energy`, `temperature`) when in doubt.
