"""CLI:  python -m unitgate "E = m * a"   |   --demo   |   --json"""
import argparse
import json
import sys

from .gate import check_equation

DEMO = ["F = m * a", "E = m * a", "E = m * c**2", "p = m * v", "v = d / t",
        "power = energy / time", "F = m * v",
        "E = 0.5*m*v**2 + m*g*h", "E = m*g*h + m*v", "d = v*t + 0.5*a*t**2"]


def _print(res, as_json):
    if as_json:
        print(json.dumps(res.to_dict(), indent=2))
        return
    print(f"{res.equation}")
    print(f"  -> {res.status}")
    if res.lhs_dim is not None:
        print(f"     lhs: {res.lhs} = {res.lhs_dim}")
        print(f"     rhs: {res.rhs} = {res.rhs_dim}")
    if res.reason:
        print(f"     {res.reason}")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="unitgate",
                                 description="Dimensional consistency check for a physics equation.")
    ap.add_argument("equation", nargs="?", help='e.g. "E = m * a"')
    ap.add_argument("--demo", action="store_true", help="run built-in examples")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)
    if args.demo:
        for eq in DEMO:
            _print(check_equation(eq), args.json)
            if not args.json:
                print()
        return 0
    if not args.equation:
        ap.print_help()
        return 2
    res = check_equation(args.equation)
    _print(res, args.json)
    # exit 1 on a dimensionally invalid equation (useful in scripts/CI)
    return 1 if res.status == "DIMENSIONALLY_INVALID" else 0


if __name__ == "__main__":
    sys.exit(main())
