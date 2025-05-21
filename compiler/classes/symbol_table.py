from dataclasses import dataclass, field
from typing import Tuple
from collections import namedtuple


EqInfo = namedtuple("EqInfo", ["expr_ast", "free_vars"])


@dataclass
class SymbolTable():
    symbols : dict = field(default_factory=dict)
    parent : 'SymbolTable' = None

    def create_var(self, key : str, type_ : str) -> None:
        if key not in self.symbols:
            self.symbols[key] = None, type_
        else:
            raise KeyError(f"Variable '{key}' already exists in symbol table.")
    
    def create_eq(self, key: str, expr_ast, free_vars: dict) -> None:
        if key in self.symbols:
            raise KeyError(f"Name '{key}' already exists in symbol table.")
        # Store the EqInfo directly
        self.symbols[key] = EqInfo(expr_ast=expr_ast, free_vars=free_vars)


    def set_var(self, key : str, tup : Tuple[int, str]) -> None:
        if key in self.symbols:
            if self.symbols[key][1] != tup[1]:
                raise TypeError(f"Type mismatch for variable '{key}'.")
            self.symbols[key] = tup
        elif self.parent:
            self.parent.set_var(key, tup)
        else:
            raise KeyError(f"Variable '{key}' not found in symbol table.")

    def get_var(self, key : str) -> Tuple[int, str]:
        if key in self.symbols:
            return self.symbols[key]
        if self.parent:
            return self.parent.get_var(key)
        raise KeyError(f"Variable '{key}' not found in symbol table.")
    
    def get_eq(self, key: str) -> EqInfo:
        val = self.symbols.get(key)
        if isinstance(val, EqInfo):
            return val
        if self.parent:
            return self.parent.get_eq(key)
        raise KeyError(f"Equation '{key}' not found in symbol table.")
