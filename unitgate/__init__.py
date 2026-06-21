"""UnitGate — catch broken physics equations before they become confident AI claims.

UnitGate checks dimensional consistency only. It does not prove physical truth
or replace experiment.
"""
from .gate import check_equation, UnitResult, VALID, INVALID, AMBIGUOUS, MALFORMED

__version__ = "0.1.0"
__all__ = ["check_equation", "UnitResult", "VALID", "INVALID", "AMBIGUOUS", "MALFORMED"]
