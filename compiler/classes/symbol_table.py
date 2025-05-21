from dataclasses import dataclass, field
from typing import Tuple, Any, Optional

@dataclass
class SymbolTable:
    symbols: dict = field(default_factory=dict)
    parent: Optional['SymbolTable'] = None 

    def create_var(self, key: str, var_type: str, value: Any = None) -> None:
        """
        Creates a new variable in the current scope.
        For 'eq' type, the 'value' is expected to be the AST Node representing the equation.
        For other types, if no explicit value is given, a default can be considered (e.g., 0 for int, False for bool).
        """
        if key in self.symbols:
            raise KeyError(f"Variable '{key}' already declared in this scope.")
        
        initial_value = value
        if value is None:
            if var_type == "int":
                initial_value = 0
            elif var_type == "bool":
                initial_value = False
            elif var_type == "eq":
                initial_value = None
        self.symbols[key] = (initial_value, var_type)

    def set_var(self, key: str, value_tuple: Tuple[Any, str]) -> None:
        """
        Sets the value of an existing variable.
        Traverses to parent scope if not found locally (standard variable assignment behavior).
        value_tuple is (new_value, new_value_type_string)
        """
        new_value, new_value_type = value_tuple

        table_to_update = self
        while table_to_update is not None:
            if key in table_to_update.symbols:
                declared_value, declared_type = table_to_update.symbols[key]
                
                if declared_type == "int" and new_value_type != "int":
                    raise TypeError(f"Type mismatch for variable '{key}'. Expected 'int', got '{new_value_type}'.")
                if declared_type == "bool" and new_value_type != "bool":
                    raise TypeError(f"Type mismatch for variable '{key}'. Expected 'bool', got '{new_value_type}'.")
                if declared_type == "eq":
                    if new_value_type != "eq_repr": 
                         pass 
                
                table_to_update.symbols[key] = (new_value, declared_type) 
                return
            table_to_update = table_to_update.parent
        
        raise KeyError(f"Variable '{key}' not found in any accessible scope for assignment.")


    def get_var(self, key: str) -> Tuple[Any, str]:
        """
        Gets the value and type of a variable.
        Traverses up the scope chain if not found locally.
        """
        current_scope = self
        while current_scope is not None:
            if key in current_scope.symbols:
                return current_scope.symbols[key]  
            current_scope = current_scope.parent
        
        raise KeyError(f"Variable '{key}' not found in any accessible scope.")

    def is_declared_locally(self, key: str) -> bool:
        """Checks if a variable is declared in the *current* (local) scope."""
        return key in self.symbols