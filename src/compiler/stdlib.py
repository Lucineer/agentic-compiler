'''Lucineer Lang Standard Library — built-in functions for the REPL.

Provides math, string, list, and agent operations that the
bytecode VM can call. Maps to deliberation opcodes.
'''
import math, random, time, hashlib
from typing import List, Dict, Any, Optional

class LucineerStdlib:
    """Standard library for Lucineer Lang."""

    def __init__(self):
        self.functions: Dict[str, callable] = {
            # Math
            "abs": lambda args: abs(args[0].value),
            "sqrt": lambda args: math.sqrt(args[0].value),
            "log": lambda args: math.log(args[0].value),
            "log10": lambda args: math.log10(args[0].value),
            "sin": lambda args: math.sin(args[0].value),
            "cos": lambda args: math.cos(args[0].value),
            "tan": lambda args: math.tan(args[0].value),
            "floor": lambda args: math.floor(args[0].value),
            "ceil": lambda args: math.ceil(args[0].value),
            "round": lambda args: round(args[0].value),
            "min": lambda args: min(a.value for a in args),
            "max": lambda args: max(a.value for a in args),
            "sum": lambda args: sum(a.value for a in args),
            "mean": lambda args: sum(a.value for a in args) / len(args),
            "clamp": lambda args: max(args[1].value, min(args[0].value, args[2].value)),
            "rand": lambda args: random.random(),
            "rand_int": lambda args: random.randint(int(args[0].value), int(args[1].value)),
            "pi": lambda args: math.pi,
            "e": lambda args: math.e,

            # String
            "len": lambda args: len(str(args[0].value)),
            "upper": lambda args: str(args[0].value).upper(),
            "lower": lambda args: str(args[0].value).lower(),
            "split": lambda args: str(args[0].value).split(str(args[1].value)) if len(args) > 1 else str(args[0].value).split(),
            "join": lambda args: str(args[0].value).join(str(a.value) for a in args[1:]),
            "strip": lambda args: str(args[0].value).strip(),
            "contains": lambda args: str(args[1].value) in str(args[0].value),
            "starts_with": lambda args: str(args[0].value).startswith(str(args[1].value)),
            "ends_with": lambda args: str(args[0].value).endswith(str(args[1].value)),
            "replace": lambda args: str(args[0].value).replace(str(args[1].value), str(args[2].value)),
            "format": lambda args: str(args[0].value).format(*(str(a.value) for a in args[1:])),

            # List
            "first": lambda args: args[0].value[0] if args[0].value else None,
            "last": lambda args: args[0].value[-1] if args[0].value else None,
            "rest": lambda args: args[0].value[1:] if args[0].value else [],
            "push": lambda args: args[0].value + [args[1].value] if isinstance(args[0].value, list) else [args[0].value, args[1].value],
            "pop": lambda args: args[0].value[:-1] if args[0].value else [],
            "reverse": lambda args: list(reversed(args[0].value)),
            "sort": lambda args: sorted(args[0].value),
            "filter": lambda args: [x for x in args[0].value if x > args[1].value] if isinstance(args[0].value, list) else [],
            "range": lambda args: list(range(int(args[0].value), int(args[1].value))),
            "zip": lambda args: list(zip(args[0].value, args[1].value)),

            # Agent
            "confidence": lambda args: args[0].confidence if hasattr(args[0], 'confidence') else 1.0,
            "set_confidence": lambda args: setattr(args[0], 'confidence', args[1].value) or args[0].confidence,
            "trust": lambda args: 0.5,  # placeholder for fleet trust
            "timestamp": lambda args: time.time(),
            "hash": lambda args: hashlib.md5(str(args[0].value).encode()).hexdigest()[:12],
        }

    def call(self, name: str, args: List[Any]) -> Optional[float]:
        fn = self.functions.get(name)
        if fn:
            try:
                return fn(args)
            except (IndexError, ValueError, TypeError, AttributeError):
                return None
        return None

    def list_functions(self) -> List[str]:
        return sorted(self.functions.keys())

    def get_category(self, name: str) -> str:
        categories = {
            "abs": "math", "sqrt": "math", "log": "math", "log10": "math",
            "sin": "math", "cos": "math", "tan": "math", "floor": "math",
            "ceil": "math", "round": "math", "min": "math", "max": "math",
            "sum": "math", "mean": "math", "clamp": "math", "rand": "math",
            "rand_int": "math", "pi": "math", "e": "math",
            "len": "string", "upper": "string", "lower": "string",
            "split": "string", "join": "string", "strip": "string",
            "contains": "string", "starts_with": "string", "ends_with": "string",
            "replace": "string", "format": "string",
            "first": "list", "last": "list", "rest": "list",
            "push": "list", "pop": "list", "reverse": "list", "sort": "list",
            "filter": "list", "range": "list", "zip": "list",
            "confidence": "agent", "set_confidence": "agent",
            "trust": "agent", "timestamp": "agent", "hash": "agent",
        }
        return categories.get(name, "unknown")


def demo():
    print("=" * 50)
    print("  LUCINEER LANG STDLIB Demo")
    print("=" * 50)

    lib = LucineerStdlib()

    # Import engine
    import importlib.util, sys
    spec = importlib.util.spec_from_file_location("engine",
        "/tmp/agentic-compiler-v2/src/compiler/engine.py")
    engine_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine_mod)
    sys.modules['compiler'] = engine_mod
    sys.modules['compiler.engine'] = engine_mod

    from compiler.engine import TensorCell

    # Test math functions
    print("\n[Math]")
    for fn, args in [("sqrt", [TensorCell(16)]), ("abs", [TensorCell(-5)]),
                     ("clamp", [TensorCell(150), TensorCell(0), TensorCell(100)]),
                     ("mean", [TensorCell(10), TensorCell(20), TensorCell(30)])]:
        result = lib.call(fn, args)
        print(f"  {fn}({', '.join(str(a.value) for a in args)}) = {result}")

    # Test string functions
    print("\n[String]")
    for fn, args in [("upper", [TensorCell("hello")]), ("contains", [TensorCell("hello world"), TensorCell("world")]),
                     ("replace", [TensorCell("hello"), TensorCell("l"), TensorCell("r")])]:
        result = lib.call(fn, args)
        print(f"  {fn}({', '.join(repr(a.value) for a in args)}) = {result}")

    # Test list functions
    print("\n[List]")
    nums = TensorCell([1, 3, 2, 5, 4])
    for fn, args in [("sort", [nums]), ("reverse", [nums]), ("mean", [nums]),
                     ("first", [nums]), ("last", [nums])]:
        result = lib.call(fn, args)
        print(f"  {fn}({nums.value}) = {result}")

    # Test agent functions
    print("\n[Agent]")
    t = TensorCell(42, confidence=0.85)
    conf = lib.call("confidence", [t])
    ts = lib.call("timestamp", [])
    print(f"  confidence(42) = {conf}")
    print(f"  timestamp() = {ts}")

    # Print all functions by category
    print(f"\nTotal stdlib functions: {len(lib.list_functions())}")
    cats: Dict[str, List[str]] = {}
    for fn in lib.list_functions():
        cat = lib.get_category(fn)
        cats.setdefault(cat, []).append(fn)
    for cat, fns in sorted(cats.items()):
        print(f"  {cat:8s}: {', '.join(fns)}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    demo()
