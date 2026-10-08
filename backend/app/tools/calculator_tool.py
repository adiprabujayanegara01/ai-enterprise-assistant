import ast
import math
import operator as op

_BIN = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.Pow: op.pow,
        ast.Mod: op.mod, ast.FloorDiv: op.floordiv}
_UN = {ast.USub: op.neg, ast.UAdd: op.pos}
_FUNCS = {"sqrt": math.sqrt, "abs": abs, "round": round, "min": min, "max": max, "log": math.log}


def safe_eval(expr: str) -> float:
    """Evaluator aritmatika aman (tanpa eval/exec)."""
    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in _BIN:
            l, r = ev(n.left), ev(n.right)
            if isinstance(n.op, ast.Pow) and abs(r) > 100:
                raise ValueError("Eksponen terlalu besar")
            return _BIN[type(n.op)](l, r)
        if isinstance(n, ast.UnaryOp) and type(n.op) in _UN:
            return _UN[type(n.op)](ev(n.operand))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in _FUNCS:
            return _FUNCS[n.func.id](*[ev(a) for a in n.args])
        raise ValueError("Ekspresi tidak diizinkan")
    expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**").replace(",", ".")
    return ev(ast.parse(expr.strip(), mode="eval"))


def calculate(ctx, expression: str):
    return {"expression": expression, "result": safe_eval(expression)}


def calculate_growth(ctx, current: float, previous: float):
    if not previous:
        return {"growth_pct": None, "note": "Nilai pembanding 0"}
    return {"current": current, "previous": previous, "difference": current - previous,
            "growth_pct": round((current - previous) / previous * 100, 2)}
