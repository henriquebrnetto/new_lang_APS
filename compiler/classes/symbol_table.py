from dataclasses import dataclass, field
from typing import Tuple, Any, Optional

# Special marker for unassigned variables
UNASSIGNED = object() 

@dataclass
class SymbolTable:
    symbols: dict = field(default_factory=dict)
    parent: Optional['SymbolTable'] = None 

    def create_var(self, key: str, var_type: str, value: Any = None) -> None:
        """
        Creates a new variable in the current scope.
        For 'eq' type, the 'value' is expected to be the AST Node representing the equation.
        For other types, if no explicit value is given, it's marked as UNASSIGNED.
        """
        if key in self.symbols:
            # Re-declaration in the same scope is usually an error.
            # For simplicity, Khwarizmi might allow shadowing if this create_var is called
            # for a new inner scope. However, for a single scope, this should be an error.
            raise KeyError(f"Variable '{key}' already declared in this scope.")
        
        initial_value = value
        # This 'value is None' check is specifically for when VarDecNode calls create_var
        # without an init_expression. If an init_expression evaluated to Python's None,
        # that would be different, but Khwarizmi types (int, bool) don't naturally yield None.
        if value is None and self.init_expression is None if hasattr(self, 'init_expression') else value is None : # Check if it was called due to no initializer
            if var_type == "int":
                initial_value = UNASSIGNED 
            elif var_type == "bool":
                initial_value = UNASSIGNED 
            elif var_type == "eq":
                # 'eq' type variables are declared and their "value" is their AST definition,
                # or None if declared like 'eq myEquation;'
                initial_value = None # Explicitly None if no AST provided yet
        
        self.symbols[key] = (initial_value, var_type)


    def set_var(self, key: str, value_tuple: Tuple[Any, str]) -> None:
        """
        Sets the value of an existing variable.
        Traverses to parent scope if not found locally.
        value_tuple is (new_value, new_value_type_string - this type is for checking, not storing)
        """
        new_value, new_value_type_for_check = value_tuple # Type is for checking compatibility
        
        table_to_update = self
        while table_to_update is not None:
            if key in table_to_update.symbols:
                _ , declared_type = table_to_update.symbols[key] # Get the originally declared type
                
                # Type Checking for assignment
                if declared_type == "int" and not isinstance(new_value, int): # Check actual Python type
                    raise TypeError(f"Type mismatch for variable '{key}'. Expected 'int', got {type(new_value).__name__}.")
                if declared_type == "bool" and not isinstance(new_value, bool): # Check actual Python type
                    raise TypeError(f"Type mismatch for variable '{key}'. Expected 'bool', got {type(new_value).__name__}.")
                if declared_type == "eq":
                    if not isinstance(new_value, Node): # Value for 'eq' must be an AST Node
                         raise TypeError(f"Assigning non-AST to 'eq' variable '{key}'. Value was {new_value}")
                
                # Store the new value, but keep the original declared_type
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
                return current_scope.symbols[key]  # Returns (stored_value, declared_type_string)
            current_scope = current_scope.parent
        
        raise KeyError(f"Variable '{key}' not found in any accessible scope.")

    def is_declared_locally(self, key: str) -> bool:
        """Checks if a variable is declared in the *current* (local) scope."""
        return key in self.symbols