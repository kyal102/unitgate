"""UnitGate: dimensional consistency check for a physics equation.

Parses ``LHS = RHS`` where each side is an expression of physics symbols
(or words) combined with ``* / + -``, parentheses, and integer powers,
computes each side's dimension with EXACT rational exponents, and reports
whether the two sides match. Terms joined by ``+``/``-`` must share one
dimension — a mismatched sum is reported as DIMENSIONALLY_INVALID with the
two clashing dimensions named.

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


# ── Expression parser: + - * / ( ) integer powers, implicit multiplication ──
# Grammar (dimensions, not values):
#   expr   := term (('+'|'-') term)*        all terms must share ONE dimension
#   term   := factor (('*'|'/'|juxtaposition) factor)*
#   factor := ('+'|'-') factor | '(' expr ')' power? | NAME power? | NUM power?
#   power  := ('**'|'^') ('+'|'-')? INT


class _UnknownSymbol(Exception):
    def __init__(self, tok: str):
        self.tok = tok


class _SumMismatch(Exception):
    def __init__(self, dim_a: Dimension, dim_b: Dimension):
        self.dim_a, self.dim_b = dim_a, dim_b


class _Malformed(Exception):
    def __init__(self, why: str):
        self.why = why


_LEX = re.compile(
    r"\s*(?:(?P<pow>\*\*|\^)|(?P<op>[+\-*/()])"
    r"|(?P<name>[A-Za-z_]+)|(?P<num>\d+(?:\.\d+)?))"
)


def _tokenize(s: str):
    toks, pos = [], 0
    s = s.rstrip()
    while pos < len(s):
        m = _LEX.match(s, pos)
        if not m:
            raise _Malformed(f"unexpected character {s[pos]!r}")
        pos = m.end()
        if m.group("pow"):
            toks.append(("POW", m.group("pow")))
        elif m.group("op"):
            toks.append(("OP", m.group("op")))
        elif m.group("name"):
            toks.append(("NAME", m.group("name")))
        else:
            toks.append(("NUM", m.group("num")))
    return toks


class _Parser:
    def __init__(self, toks):
        self.toks, self.i = toks, 0

    def _peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else (None, None)

    def _next(self):
        t = self._peek()
        self.i += 1
        return t

    def parse(self) -> Dimension:
        d = self._expr()
        if self.i < len(self.toks):
            raise _Malformed(f"unexpected {self.toks[self.i][1]!r} after expression")
        return d

    def _expr(self) -> Dimension:
        d = self._term()
        while self._peek() in (("OP", "+"), ("OP", "-")):
            self._next()
            d2 = self._term()
            if d != d2:
                raise _SumMismatch(d, d2)
        return d

    def _term(self) -> Dimension:
        d = self._factor()
        while True:
            kind, val = self._peek()
            if kind == "OP" and val in ("*", "/"):
                self._next()
                d2 = self._factor()
                d = d * d2 if val == "*" else d / d2
            elif kind in ("NAME", "NUM") or (kind == "OP" and val == "("):
                d = d * self._factor()       # juxtaposition: "m a" = m * a
            else:
                return d

    def _factor(self) -> Dimension:
        kind, val = self._peek()
        if kind == "OP" and val in ("+", "-"):   # unary sign
            self._next()
            return self._factor()
        if kind == "OP" and val == "(":
            self._next()
            d = self._expr()
            if self._next() != ("OP", ")"):
                raise _Malformed("missing ')'")
            return self._power_suffix(d)
        if kind == "NUM":
            self._next()
            return self._power_suffix(DIMENSIONLESS)
        if kind == "NAME":
            self._next()
            d = _token_dimension(val)
            if d is None:
                raise _UnknownSymbol(val)
            return self._power_suffix(d)
        if kind is None:
            raise _Malformed("unexpected end of expression")
        raise _Malformed(f"expected a symbol, number or '(' (got {val!r})")

    def _power_suffix(self, d: Dimension) -> Dimension:
        if self._peek()[0] != "POW":
            return d
        self._next()
        sign = 1
        kind, val = self._peek()
        if kind == "OP" and val in ("+", "-"):
            self._next()
            sign = -1 if val == "-" else 1
            kind, val = self._peek()
        if kind != "NUM" or "." in val:
            raise _Malformed("exponent must be an integer (e.g. v**2, t**-1)")
        self._next()
        return d ** (sign * int(val))


def _side_dimension(side: str) -> Dimension:
    """Compute the dimension of one side. Raises _UnknownSymbol / _SumMismatch /
    _Malformed on failure."""
    s = side.replace("·", "*").replace("×", "*").strip()
    if not s:
        raise _Malformed("empty side")
    return _Parser(_tokenize(s)).parse()


def check_equation(equation: str) -> UnitResult:
    """Check the dimensional consistency of ``LHS = RHS``."""
    eq = (equation or "").strip()
    if eq.count("=") != 1:
        return UnitResult(MALFORMED, eq, reason="expected exactly one '=' (form: LHS = RHS)")
    lhs_s, rhs_s = (p.strip() for p in eq.split("="))
    if not lhs_s or not rhs_s:
        return UnitResult(MALFORMED, eq, reason="both sides of '=' must be non-empty")
    dims = []
    for label, s in (("left", lhs_s), ("right", rhs_s)):
        try:
            dims.append(_side_dimension(s))
        except _UnknownSymbol as e:
            return UnitResult(AMBIGUOUS, eq, lhs=lhs_s, rhs=rhs_s,
                              reason=f"unknown/ambiguous symbol: {e.tok!r} (add it or use a known symbol)")
        except _SumMismatch as e:
            return UnitResult(INVALID, eq, lhs=lhs_s, rhs=rhs_s,
                              reason=(f"terms added on the {label} side do not share one dimension: "
                                      f"{e.dim_a.display()} vs {e.dim_b.display()} — "
                                      "every term in a sum must have the same dimension"))
        except _Malformed as e:
            return UnitResult(MALFORMED, eq, lhs=lhs_s, rhs=rhs_s, reason=e.why)
    lhs_dim, rhs_dim = dims
    ld, rd = lhs_dim.display(), rhs_dim.display()
    if lhs_dim == rhs_dim:
        return UnitResult(VALID, eq, lhs=lhs_s, rhs=rhs_s, lhs_dim=ld, rhs_dim=rd,
                          reason="both sides have the same dimension")
    return UnitResult(INVALID, eq, lhs=lhs_s, rhs=rhs_s, lhs_dim=ld, rhs_dim=rd,
                      reason=f"{lhs_s} has dimension {ld}, but {rhs_s} has dimension {rd}")
