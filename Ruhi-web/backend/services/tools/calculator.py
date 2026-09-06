
import ast
import math
import operator
from typing import Dict, Any, Callable, Type
from backend.services.tools.base import BaseTool

# Safe operators for calculator separated by arity
_ALLOWED_BIN_OPS: Dict[Type[ast.AST], Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_ALLOWED_UNARY_OPS: Dict[Type[ast.AST], Callable[[Any], Any]] = {
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_ALLOWED_CONSTANTS: Dict[str, float] = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
}

_ALLOWED_FUNCTIONS: Dict[str, Any] = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
    "round": round,
    "ceil": math.ceil,
    "floor": math.floor,
}


def _safe_eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Unsupported constant type: {type(node.value)}")
    
    if isinstance(node, ast.Name):
        if node.id in _ALLOWED_CONSTANTS:
            return _ALLOWED_CONSTANTS[node.id]
        raise ValueError(f"Variable '{node.id}' is not permitted")

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type in _ALLOWED_UNARY_OPS:
            operand = _safe_eval_node(node.operand)
            return float(_ALLOWED_UNARY_OPS[op_type](operand))
        raise ValueError(f"Unsupported unary operator: {op_type}")

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type in _ALLOWED_BIN_OPS:
            left = _safe_eval_node(node.left)
            right = _safe_eval_node(node.right)
            if op_type == ast.Pow and right > 1000:
                raise ValueError("Exponent too large")
            return float(_ALLOWED_BIN_OPS[op_type](left, right))
        raise ValueError(f"Unsupported binary operator: {op_type}")

    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in _ALLOWED_FUNCTIONS:
            fn = _ALLOWED_FUNCTIONS[node.func.id]
            args = [_safe_eval_node(arg) for arg in node.args]
            return float(fn(*args))
        raise ValueError("Function call is not permitted")

    raise ValueError(f"Unsupported AST node: {type(node)}")


class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = "Safely evaluate mathematical and arithmetic expressions."
    category: str = "calculation"
    requires_desktop: bool = False

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate (e.g. 'sqrt(144) + 25 * 4')"
                }
            },
            "required": ["expression"]
        }

    async def execute(self, expression: str = "", **kwargs: Any) -> Dict[str, Any]:
        if not expression:
            return {
                "expression": "",
                "error": "Expression parameter is required.",
                "success": False
            }
        try:
            expr_clean = expression.strip()
            parsed = ast.parse(expr_clean, mode="eval")
            result = _safe_eval_node(parsed.body)
            return {
                "expression": expr_clean,
                "result": result,
                "success": True
            }
        except Exception as e:
            return {
                "expression": expression,
                "error": f"Calculation error: {str(e)}",
                "success": False
            }
