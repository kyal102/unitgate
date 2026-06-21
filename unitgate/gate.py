"""UnitGate: dimensional consistency check for a physics equation.

Parses ``LHS = RHS`` where each side is a product/quotient of physics symbols
(or words) with optional integer powers, computes each side's dimension with
EXACT rational exponents, and reports whether the two sides match.

UnitGate checks dimensional consistency ONLY. It does not prove physical truth
or replace experiment.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .dimensions import Dimension, DIMENSIONLESS, lookup_unit

# Common physics symbols -> the unit name UnitGate knows (see dimensions.UNIT_TABLE).
# Only reasonably unambiguous symbols are mapped; anything else is reported as
# AMBIGUOUS rather than guessed.
SYMBOL_MAP = {
    "E": "energy", "KE": "energy", "PE": "energy", "W": "work", "Q": "heat",
    "F": "force", "m": "mass", "M": "mass",
    "a": "acceleration", "g": "acceleration",
    "v": "velocity", "u": "velocity", "c": "velocity",
    "p": "momentum", "L": "angular_momentum",
    "P": "power",
    "t": "time", "T": "time",
    "x": "distance", "d": "distance", "r": "distance", "h": "distance",
    "rho": "density", "f": "frequency",
}

VALID = "DIMENSIONALLY_VALID"
INVALID = "DIMENSIONALLY_INVALID"
AMBIGUOUS = "AMBIGUOUS_NEEDS_CLARIFICATION"
MALFORMED = "MALFORMED_INPUT"


@dataclass
class UnitResult:
    status: str
    equation: str
    lhs: str = ""
    rhs: str = ""
    lhs_dim: Optional[str] = None
    rhs_dim: Optional[str] = None
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "tool": "unitgate", "status": self.status, "equation": self.equation,
            "lhs": self.lhs, "rhs": self.rhs,
            "lhs_dimension": self.lhs_dim, "rhs_dimension": self.rhs_dim,
            "reason": self.reason,
            "public_wording": ("UnitGate checks dimensional consistency only. "
                               "It does not prove physical truth or replace experiment."),
        }


def _token_dimension(tok: str) -> Optional[Dimension]:
    """Resolve one token (symbol, word, or number) to a Dimension. None = unknown."""
    tok = tok.strip()
    if not tok:
        return None
    if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", tok):   # a pure number is dimensionless
        return DIMENSIONLESS
    if tok in SYMBOL_MAP:                          # exact-case symbol (E, m, F, ...)
        return lookup_unit(SYMBOL_MAP[tok])
    word = lookup_unit(tok)                        # word form (energy, mass, ...)
    if word is not None:
        return word
    return None


# One token = a base (symbol/word/number) with an optional ^N or **N power,
# OR a single * or / operator. Tokenizing (not splitting) keeps ** intact.
_TOKEN = re.compile(r"([A-Za-z_]+|\d+(?:\.\d+)?)(?:\s*(?:\^|\*\*)\s*([+-]?\d+))?|([*/])")


def _side_dimension(side: str):
    """Compute the dimension of one side (product/quotient of tokens).
    Returns (Dimension, None) on success or (None, bad_token) on failure."""
    s = side.replace("·", "*").replace("×", "*").strip()
    if not s:
        return None, side
    # Lite tool: products/quotients only. Sums/parentheses are out of scope.
    if re.search(r"[+()]|(?<![*\s])-|-(?![\d])", s):
        return None, s
    dim = DIMENSIONLESS
    op = "*"
    first = True
    covered = 0
    for m in _TOKEN.finditer(s):
        if m.start() != covered and s[covered:m.start()].strip():
            return None, s.strip()          # stray characters between tokens
        covered = m.end()
        if m.group(3):                       # operator
            op = m.group(3)
            continue
        base, exp = m.group(1), m.group(2)
        d = _token_dimension(base)
        if d is None:
            return None, base
        if exp:
            d = d ** int(exp)
        dim = d if first else (dim * d if op == "*" else dim / d)
        first = False
    if s[covered:].strip():
        return None, s.strip()               # trailing stray characters
    return (dim, None) if not first else (None, side)


def check_equation(equation: str) -> UnitResult:
    """Check the dimensional consistency of ``LHS = RHS``."""
    eq = (equation or "").strip()
    if eq.count("=") != 1:
        return UnitResult(MALFORMED, eq, reason="expected exactly one '=' (form: LHS = RHS)")
    lhs_s, rhs_s = (p.strip() for p in eq.split("="))
    if not lhs_s or not rhs_s:
        return UnitResult(MALFORMED, eq, reason="both sides of '=' must be non-empty")
    lhs_dim, bad_l = _side_dimension(lhs_s)
    rhs_dim, bad_r = _side_dimension(rhs_s)
    if lhs_dim is None or rhs_dim is None:
        bad = bad_l or bad_r
        return UnitResult(AMBIGUOUS, eq, lhs=lhs_s, rhs=rhs_s,
                          reason=f"unknown/ambiguous symbol: {bad!r} (add it or use a known symbol)")
    ld, rd = lhs_dim.display(), rhs_dim.display()
    if lhs_dim == rhs_dim:
        return UnitResult(VALID, eq, lhs=lhs_s, rhs=rhs_s, lhs_dim=ld, rhs_dim=rd,
                          reason="both sides have the same dimension")
    return UnitResult(INVALID, eq, lhs=lhs_s, rhs=rhs_s, lhs_dim=ld, rhs_dim=rd,
                      reason=f"{lhs_s} has dimension {ld}, but {rhs_s} has dimension {rd}")
