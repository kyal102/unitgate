# UnitGate examples

| Command | Result |
|---|---|
| `python -m unitgate "F = m * a"` | DIMENSIONALLY_VALID |
| `python -m unitgate "E = m * a"` | DIMENSIONALLY_INVALID |
| `python -m unitgate "E = m * c**2"` | DIMENSIONALLY_VALID |
| `python -m unitgate "p = m * v"` | DIMENSIONALLY_VALID |
| `python -m unitgate "v = d / t"` | DIMENSIONALLY_VALID |
| `python -m unitgate "power = energy / time"` | DIMENSIONALLY_VALID |
| `python -m unitgate "F = m * v"` | DIMENSIONALLY_INVALID |
| `python -m unitgate "E = zzz * a"` | AMBIGUOUS_NEEDS_CLARIFICATION |

JSON: `python -m unitgate --json "E = m * a"` returns `{tool, status, equation, lhs_dimension, rhs_dimension, reason, public_wording}`.
