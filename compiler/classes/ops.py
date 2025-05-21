from classes.node import Node
from classes.symbol_table import SymbolTable, UNASSIGNED # Ensure UNASSIGNED is imported
from typing import List, Any, Tuple, Set, Dict, Optional
from dataclasses import dataclass, field

class KhwarizmiRuntimeError(Exception):
    pass

#----------------------------------------------------------------------
# HELPER FUNCTIONS (substitute_ast, ast_node_to_string, simplify_arithmetic_ast, collect_terms_linear, TermAnalysisResult)
# These are assumed to be present and correct as per khwarizmi_ops_py_final_solve / your current file.
# For brevity, their full code is not repeated here, but their correct interaction with UNASSIGNED is key.
# Specifically, ast_node_to_string and simplify_arithmetic_ast need to handle UNASSIGNED from get_var.
#----------------------------------------------------------------------

def substitute_ast(node: Optional[Node], substitutions: Dict[str, Any], symbol_table: SymbolTable) -> Optional[Node]:
    if node is None: return None
    if not isinstance(node, Node):
        raise TypeError(f"substitute_ast expects a Node instance, got {type(node)}")
    if isinstance(node, IdentifierNode):
        var_name = node.value
        if var_name in substitutions:
            value_to_sub = substitutions[var_name]
            if isinstance(value_to_sub, int): return IntLiteralNode(value_to_sub)
            elif isinstance(value_to_sub, bool): return BoolLiteralNode(value_to_sub)
            else: raise KhwarizmiRuntimeError(f"Substitution for '{var_name}' has unsupported type: {type(value_to_sub)}. Expected int or bool.")
        else: return IdentifierNode(node.value) # Return a new instance
    elif isinstance(node, (IntLiteralNode, BoolLiteralNode)):
        return type(node)(node.value) # Return a new instance
    elif isinstance(node, BinOpNode):
        new_left_child = substitute_ast(node.children[0], substitutions, symbol_table)
        new_right_child = substitute_ast(node.children[1], substitutions, symbol_table)
        return BinOpNode(node.value, [new_left_child, new_right_child])
    elif isinstance(node, UnOpNode):
        new_operand = substitute_ast(node.children[0], substitutions, symbol_table)
        return UnOpNode(node.value, [new_operand])
    elif isinstance(node, EquationNode):
        new_symbolic_expr = substitute_ast(node.symbolic_expression, substitutions, symbol_table)
        return EquationNode(new_symbolic_expr)
    else: # Fallback for other node types
        new_children = []
        if hasattr(node, 'children') and isinstance(node.children, list):
            for child in node.children:
                if isinstance(child, Node): new_children.append(substitute_ast(child, substitutions, symbol_table))
                else: new_children.append(child)
        try:
            if hasattr(node, 'children'): return type(node)(node.value, new_children)
            else: return type(node)(node.value)
        except TypeError: return node

def ast_node_to_string(node: Any, symbol_table: SymbolTable, parent_op_precedence: int = 0) -> str:
    if not isinstance(node, Node):
        if isinstance(node, bool): return str(node).lower()
        return str(node)
    if isinstance(node, IdentifierNode):
        try:
            value, type_str = symbol_table.get_var(node.value)
            if value is UNASSIGNED: # <<< POINT 2: Correctly print name if UNASSIGNED
                return node.value 
            if type_str == "eq": return ast_node_to_string(value, symbol_table)
            elif type_str == "bool": return str(value).lower()
            if not isinstance(value, Node): return str(value)
            else: return node.value # Fallback if an AST node was stored for a non-eq var
        except KeyError: return node.value # Free symbolic variable (not in symbol_table at all)
    elif isinstance(node, IntLiteralNode): return str(node.value)
    elif isinstance(node, BoolLiteralNode): return str(node.value).lower()
    elif isinstance(node, BinOpNode):
        left_str = ast_node_to_string(node.children[0], symbol_table)
        right_str = ast_node_to_string(node.children[1], symbol_table)
        return f"({left_str} {node.value} {right_str})"
    elif isinstance(node, UnOpNode):
        operand_str = ast_node_to_string(node.children[0], symbol_table)
        if isinstance(node.children[0], (IntLiteralNode, IdentifierNode)): return f"{node.value}{operand_str}"
        else: return f"{node.value}({operand_str})"
    elif isinstance(node, EquationNode): return ast_node_to_string(node.symbolic_expression, symbol_table)
    else:
        val_attr = node.value if hasattr(node, 'value') else type(node).__name__
        return f"<AST:{type(node).__name__}:{val_attr}>"

def simplify_arithmetic_ast(node: Node, symbol_table: SymbolTable) -> int:
    if not isinstance(node, Node): raise KhwarizmiRuntimeError(f"Cannot simplify non-Node type: {type(node)}")
    if isinstance(node, IntLiteralNode): return node.value
    elif isinstance(node, IdentifierNode):
        try:
            value, type_str = symbol_table.get_var(node.value)
            if value is UNASSIGNED: # <<< POINT 3: Error if UNASSIGNED during simplification
                raise KhwarizmiRuntimeError(f"Cannot simplify: Variable '{node.value}' is unassigned.")
            if type_str == "int":
                if not isinstance(value, int): raise KhwarizmiRuntimeError(f"Var '{node.value}' is 'int' but not int value: {value}")
                return value
            else: raise KhwarizmiRuntimeError(f"Cannot simplify: Var '{node.value}' is '{type_str}', not 'int'.")
        except KeyError: raise KhwarizmiRuntimeError(f"Cannot simplify: Symbolic var '{node.value}' has no value in this context.")
    elif isinstance(node, BinOpNode):
        if node.value not in ['+', '-', '*', '/']: raise KhwarizmiRuntimeError(f"Cannot simplify: Non-arithmetic op '{node.value}'.")
        left_val = simplify_arithmetic_ast(node.children[0], symbol_table)
        right_val = simplify_arithmetic_ast(node.children[1], symbol_table)
        if node.value == '+': return left_val + right_val
        if node.value == '-': return left_val - right_val
        if node.value == '*': return left_val * right_val
        if node.value == '/':
            if right_val == 0: raise ZeroDivisionError("Khwarizmi: Division by zero during simplification.")
            if left_val % right_val != 0: raise KhwarizmiRuntimeError(f"Cannot simplify: Division {left_val}/{right_val} non-integer for Khwarizmi 'int' type.")
            return left_val // right_val
    elif isinstance(node, UnOpNode):
        if node.value == '-':
            operand_val = simplify_arithmetic_ast(node.children[0], symbol_table)
            return -operand_val
        else: raise KhwarizmiRuntimeError(f"Cannot simplify: Non-arithmetic unary op '{node.value}'.")
    else: raise KhwarizmiRuntimeError(f"Cannot simplify: Encountered non-arithmetic AST node type '{type(node).__name__}'.")

@dataclass
class TermAnalysisResult: # As defined before
    coeff_sum: int = 0; const_sum: int = 0; is_linear: bool = True
    other_free_vars: Set[str] = field(default_factory=set)

def collect_terms_linear(node: Node, target_var_name: str, eval_scope: SymbolTable) -> TermAnalysisResult:
    res = TermAnalysisResult()
    if isinstance(node, IntLiteralNode): res.const_sum = node.value; return res
    elif isinstance(node, IdentifierNode):
        if node.value == target_var_name: res.coeff_sum = 1
        else:
            try:
                val, type_str = eval_scope.get_var(node.value)
                if val is UNASSIGNED: # <<< POINT 4: Add to other_free_vars if UNASSIGNED
                    res.is_linear = True # Still linear, but this var is free
                    res.other_free_vars.add(node.value)
                elif type_str == "int": res.const_sum = val
                else: res.is_linear = False; res.other_free_vars.add(node.value)
            except KeyError: # Undeclared in eval_scope means it's free for this analysis
                res.is_linear = True 
                res.other_free_vars.add(node.value)
        return res
    # ... (rest of collect_terms_linear as in khwarizmi_ops_py_v8_collect_terms) ...
    elif isinstance(node, UnOpNode):
        if node.value == '-':
            op_an = collect_terms_linear(node.children[0], target_var_name, eval_scope)
            res.coeff_sum = -op_an.coeff_sum; res.const_sum = -op_an.const_sum
            res.is_linear = op_an.is_linear; res.other_free_vars.update(op_an.other_free_vars)
        else: res.is_linear = False; res.other_free_vars.update(node.collect_identifiers() - {target_var_name})
        return res
    elif isinstance(node, BinOpNode):
        op = node.value
        left_an = collect_terms_linear(node.children[0], target_var_name, eval_scope)
        right_an = collect_terms_linear(node.children[1], target_var_name, eval_scope)
        res.is_linear = left_an.is_linear and right_an.is_linear
        res.other_free_vars.update(left_an.other_free_vars); res.other_free_vars.update(right_an.other_free_vars)
        if not res.is_linear: return res
        if op == '+':
            res.coeff_sum = left_an.coeff_sum + right_an.coeff_sum; res.const_sum = left_an.const_sum + right_an.const_sum
        elif op == '-':
            res.coeff_sum = left_an.coeff_sum - right_an.coeff_sum; res.const_sum = left_an.const_sum - right_an.const_sum
        elif op == '*':
            if left_an.coeff_sum != 0 and right_an.coeff_sum != 0: res.is_linear = False
            elif left_an.coeff_sum != 0:
                if right_an.coeff_sum != 0: res.is_linear = False
                else: res.coeff_sum = left_an.coeff_sum * right_an.const_sum; res.const_sum = left_an.const_sum * right_an.const_sum
            elif right_an.coeff_sum != 0:
                if left_an.coeff_sum != 0: res.is_linear = False
                else: res.coeff_sum = right_an.coeff_sum * left_an.const_sum; res.const_sum = right_an.const_sum * left_an.const_sum
            else: res.const_sum = left_an.const_sum * right_an.const_sum
        elif op == '/':
            if right_an.coeff_sum != 0: res.is_linear = False
            else:
                if right_an.const_sum == 0: raise ZeroDivisionError("Khwarizmi: Division by zero constant in symbolic term collection.")
                if (left_an.coeff_sum % right_an.const_sum != 0) or (left_an.const_sum % right_an.const_sum != 0): res.is_linear = False
                else: res.coeff_sum = left_an.coeff_sum // right_an.const_sum; res.const_sum = left_an.const_sum // right_an.const_sum
        else: res.is_linear = False; res.other_free_vars.update(node.collect_identifiers() - {target_var_name})
        return res
    else:
        res.is_linear = False; res.other_free_vars.update(node.collect_identifiers() - {target_var_name})
        return res

# --- AST Node Classes ---

class ProgramNode(Node):
    def evaluate(self, symbol_table: SymbolTable):
        try: return self.children[0].evaluate(symbol_table)
        except KhwarizmiRuntimeError as e: print(f"Runtime Error: {e}")
        except KeyError as e: print(f"Runtime Error (NameError): Variable '{e.args[0]}' not found.")
        except TypeError as e: print(f"Runtime Error (TypeError): {e}")
        except ZeroDivisionError: print("Runtime Error: Division by zero.")
        except Exception as e: print(f"Unexpected Runtime Error: {type(e).__name__} - {e}")

class BlockNode(Node):
    def evaluate(self, symbol_table: SymbolTable):
        last_stmt_val = (None, "void"); 
        for stmt_node in self.children: stmt_node.evaluate(symbol_table)
        return last_stmt_val

class TypeNode(Node):
    def evaluate(self, symbol_table: SymbolTable): return self.value
    def collect_identifiers(self) -> Set[str]: return set()

class VarDecNode(Node):
    def __init__(self, type_name_str: str, var_name: str, init_expression: Optional[Node] = None):
        super().__init__(value=var_name); self.type_name_str = type_name_str; self.var_name = var_name
        self.init_expression = init_expression; self.children = [self.init_expression] if self.init_expression else []
    def evaluate(self, symbol_table: SymbolTable):
        if self.type_name_str == "eq":
            if self.init_expression: symbol_table.create_var(self.var_name, self.type_name_str, self.init_expression)
            else: symbol_table.create_var(self.var_name, self.type_name_str, None) # Store None if eq x;
        elif self.init_expression:
            init_val, init_type = self.init_expression.evaluate(symbol_table)
            # If init_val itself is an AST node (e.g. from a symbolic expression that became eq_repr)
            # and we are declaring an int/bool, this is a type error.
            if isinstance(init_val, Node) and init_type == "eq_repr":
                 raise KhwarizmiRuntimeError(f"Cannot assign symbolic expression to non-eq variable '{self.var_name}'.")

            if self.type_name_str == "int" and init_type != "int": raise KhwarizmiRuntimeError(f"Type mismatch for '{self.var_name}'. Expected 'int', got '{init_type}'.")
            if self.type_name_str == "bool" and init_type != "bool": raise KhwarizmiRuntimeError(f"Type mismatch for '{self.var_name}'. Expected 'bool', got '{init_type}'.")
            symbol_table.create_var(self.var_name, self.type_name_str, init_val)
        else: # No initializer, SymbolTable.create_var will use UNASSIGNED for int/bool
            symbol_table.create_var(self.var_name, self.type_name_str, None) # Pass None, ST handles UNASSIGNED
        return None, "void"
    def collect_identifiers(self) -> Set[str]:
        ids: Set[str] = set(); 
        if self.init_expression and isinstance(self.init_expression, Node): ids.update(self.init_expression.collect_identifiers())
        return ids

class AssignmentNode(Node):
    def evaluate(self, symbol_table: SymbolTable):
        var_name = self.children[0].value; _ , declared_type = symbol_table.get_var(var_name)
        if declared_type == "eq":
            # RHS for 'eq' assignment is the AST itself, not its evaluated value
            new_equation_ast = self.children[1] 
            symbol_table.set_var(var_name, (new_equation_ast, "eq"))
            return new_equation_ast, "eq_repr"
        else:
            new_value, new_type = self.children[1].evaluate(symbol_table)
            if isinstance(new_value, Node) and new_type == "eq_repr":
                 raise KhwarizmiRuntimeError(f"Cannot assign symbolic expression to non-eq variable '{var_name}'.")
            if declared_type == "int" and new_type != "int": raise KhwarizmiRuntimeError(f"Type mismatch for '{var_name}'. Expected 'int', got '{new_type}'.")
            if declared_type == "bool" and new_type != "bool": raise KhwarizmiRuntimeError(f"Type mismatch for '{var_name}'. Expected 'bool', got '{new_type}'.")
            symbol_table.set_var(var_name, (new_value, declared_type)); return new_value, declared_type
    def collect_identifiers(self) -> Set[str]:
        ids: Set[str] = set()
        if isinstance(self.children[0], Node): ids.update(self.children[0].collect_identifiers())
        if len(self.children) > 1 and isinstance(self.children[1], Node): ids.update(self.children[1].collect_identifiers())
        return ids

class BinOpNode(Node):
    def evaluate(self, symbol_table: SymbolTable) -> Tuple[Any, str]:
        left_child = self.children[0]; right_child = self.children[1]
        # Evaluate children. If a child is symbolic (e.g. unassigned var), its evaluate will return (AST_Node, "eq_repr")
        left_val, left_type = left_child.evaluate(symbol_table)
        right_val, right_type = right_child.evaluate(symbol_table)
        
        op = self.value

        # If any part of the binary operation is symbolic, the whole operation becomes symbolic
        if left_type == "eq_repr" or right_type == "eq_repr":
            # Exception: for '==' or '!=' comparisons, if one side is eq_repr and other is concrete int/bool,
            # the comparison itself is symbolic (e.g., myEq == 0)
            if op in ["==", "!="] and (left_type == "eq_repr" or right_type == "eq_repr"):
                 # Ensure the non-eq_repr side is int or bool if it's concrete
                if left_type != "eq_repr" and left_type not in ["int", "bool"]:
                    raise KhwarizmiRuntimeError(f"Cannot compare symbolic expression with type '{left_type}' using '{op}'.")
                if right_type != "eq_repr" and right_type not in ["int", "bool"]:
                    raise KhwarizmiRuntimeError(f"Cannot compare symbolic expression with type '{right_type}' using '{op}'.")
                return self, "eq_repr" # The comparison expression itself is symbolic
            # For other ops like +, -, *, /, &&, ||, if one side is symbolic, the result is symbolic
            return self, "eq_repr"

        # Both operands are concrete, proceed with normal evaluation
        if op in ['+', '-', '*', '/']:
            if not (left_type == "int" and right_type == "int"): raise KhwarizmiRuntimeError(f"Arithmetic '{op}' needs 'int's, got '{left_type}', '{right_type}'.")
            if op == '+': return left_val + right_val, "int"
            if op == '-': return left_val - right_val, "int"
            if op == '*': return left_val * right_val, "int"
            if op == '/':
                if right_val == 0: raise ZeroDivisionError("Khwarizmi: Division by zero.")
                return left_val // right_val, "int"
        elif op in ["&&", "||"]:
            if not (left_type == "bool" and right_type == "bool"): raise KhwarizmiRuntimeError(f"Logical '{op}' needs 'bool's, got '{left_type}', '{right_type}'.")
            if op == '&&': return left_val and right_val, "bool"
            if op == '||': return left_val or right_val, "bool"
        elif op in ["==", "!=", "<", ">", "<=", ">="]:
            can_compare = (left_type == "int" and right_type == "int") or \
                          (left_type == "bool" and right_type == "bool" and op in ["==", "!="])
            if not can_compare: raise KhwarizmiRuntimeError(f"Comparison '{op}' needs compatible types, got '{left_type}', '{right_type}'.")
            if op == '==': return left_val == right_val, "bool"
            if op == '!=': return left_val != right_val, "bool"
            if op == '<': return left_val < right_val, "bool"
            if op == '>': return left_val > right_val, "bool"
            if op == '<=': return left_val <= right_val, "bool"
            if op == '>=': return left_val >= right_val, "bool"
        else: raise KhwarizmiRuntimeError(f"Unknown binary operator: {op}")


class UnOpNode(Node):
    def evaluate(self, symbol_table: SymbolTable) -> Tuple[Any, str]:
        operand_child = self.children[0]; op = self.value
        val, type_str = operand_child.evaluate(symbol_table) # Evaluate operand first

        if type_str == "eq_repr": # If operand is symbolic, result is symbolic
            return self, "eq_repr"
            
        if op == '-':
            if type_str != "int":
                raise KhwarizmiRuntimeError(f"Unary minus needs 'int', got '{type_str}'.")
            return -val, "int"
        
        elif op == '!':
            if type_str != "bool":
                raise KhwarizmiRuntimeError(f"Logical NOT needs 'bool', got '{type_str}'.")
            return not val, "bool"
        else: raise KhwarizmiRuntimeError(f"Unknown unary operator: {op}")


class IntLiteralNode(Node):
    def evaluate(self, symbol_table: SymbolTable): return self.value, "int"
    def collect_identifiers(self) -> Set[str]: return set()


class BoolLiteralNode(Node):
    def evaluate(self, symbol_table: SymbolTable): return self.value, "bool"
    def collect_identifiers(self) -> Set[str]: return set()


class IdentifierNode(Node):
    def evaluate(self, symbol_table: SymbolTable):
        try:
            value, type_str = symbol_table.get_var(self.value)
            if value is UNASSIGNED: # <<< POINT 1: Correctly return (self, "eq_repr")
                return self, "eq_repr" 
            if type_str == "eq": 
                return value, "eq_repr" # 'value' is the AST of the equation
            return value, type_str 
        except KeyError:
            # If truly undeclared, it's an error unless this evaluate is in a special symbolic context
            # For now, this implies an undeclared variable error if reached.
            # The BinOp/UnOp evaluate methods will catch this KeyError for their children
            # and then return (self, "eq_repr") if a child was undeclared.
            raise KhwarizmiRuntimeError(f"Undeclared identifier '{self.value}' used.")
            # To allow undeclared IDs to be symbolic everywhere:
            # return self, "eq_repr" 
    def collect_identifiers(self) -> Set[str]: return {self.value}


class InputNode(Node):
    def evaluate(self, symbol_table: SymbolTable):
        while True:
            try: val_str = input(); return int(val_str), "int"
            except ValueError: print("Invalid input. Please enter an integer.")
            except EOFError: raise KhwarizmiRuntimeError("EOF reached while expecting input.")
    def collect_identifiers(self) -> Set[str]: return set()


class EquationNode(Node):
    def __init__(self, symbolic_expression_node: Node): super().__init__(value="equation_wrapper"); self.symbolic_expression = symbolic_expression_node; self.children = [symbolic_expression_node]
    def evaluate(self, symbol_table: SymbolTable): return self.symbolic_expression, "eq_repr"
    def get_symbolic_expr(self) -> Node: return self.symbolic_expression


class ArgumentListNode(Node):
    def evaluate(self, symbol_table: SymbolTable) -> List[Tuple[Any, str]]:
        evaluated_args = []; 
        for arg_node in self.children: val, type_str = arg_node.evaluate(symbol_table); evaluated_args.append((val, type_str))
        return evaluated_args
    

class PrintCmdNode(Node):
    def evaluate(self, symbol_table: SymbolTable):
        arg_list_node = self.children[0]; evaluated_args = arg_list_node.evaluate(symbol_table)
        print_values = []
        for val, type_str in evaluated_args:
            if type_str == "bool": print_values.append(str(val).lower())
            elif type_str == "eq_repr": print_values.append(f"<Equation: {ast_node_to_string(val, symbol_table)} >")
            elif val is UNASSIGNED: print_values.append("<unassigned>") # Print unassigned int/bool
            else: print_values.append(str(val))
        print(" ".join(print_values)); return None, "void"


class ShowCmdNode(Node):
    def evaluate(self, symbol_table: SymbolTable):
        arg_list_node = self.children[0]
        if not arg_list_node.children: raise KhwarizmiRuntimeError("show() command requires at least one argument.")
        first_arg_node = arg_list_node.children[0]; effective_ast_to_display: Node; original_eq_name_for_print: Optional[str] = None
        
        # Evaluate the first argument to determine its nature (is it an 'eq' var, a comparison, or other symbolic expr?)
        val_or_ast_of_first_arg, type_of_first_arg = first_arg_node.evaluate(symbol_table)

        if type_of_first_arg == "eq_repr": # This means it's symbolic (an eq var, an unassigned var, or a symbolic BinOp)
            effective_ast_to_display = val_or_ast_of_first_arg # This is already the AST node
            if isinstance(first_arg_node, IdentifierNode): # If show(myEq), where myEq is 'eq' or unassigned
                original_eq_name_for_print = first_arg_node.value
        # Removed: elif type_of_first_arg == "bool" and isinstance(first_arg_node, BinOpNode) ...
        # The above "eq_repr" check for BinOpNode should cover comparisons like `myEq == 0` or `x > 5`
        # because their .evaluate() will return (self, "eq_repr") if they contain symbolic parts.
        else: 
            # If the first argument evaluated to a concrete int/bool, it's not what 'show' is for.
            raise KhwarizmiRuntimeError(f"First argument to show() must resolve to a symbolic equation or expression. Got concrete type '{type_of_first_arg}'.")
        
        substitutions_map: Dict[str, int] = {}
        for subst_arg_node in arg_list_node.children[1:]:
            if not (isinstance(subst_arg_node, BinOpNode) and subst_arg_node.value == "==" and isinstance(subst_arg_node.children[0], IdentifierNode)):
                raise KhwarizmiRuntimeError("Invalid substitution format in show(). Expected 'IDENTIFIER == integer_expression'.")
            var_to_sub_name = subst_arg_node.children[0].value; val_expr_node = subst_arg_node.children[1]
            sub_val, sub_type = val_expr_node.evaluate(symbol_table)
            if sub_type != "int": raise KhwarizmiRuntimeError(f"Substitution value for '{var_to_sub_name}' in show() must be an integer, got {sub_type}.")
            substitutions_map[var_to_sub_name] = sub_val
        
        ast_after_direct_substitutions = substitute_ast(effective_ast_to_display, substitutions_map, symbol_table)
        
        potential_free_vars_in_final_ast = ast_after_direct_substitutions.collect_identifiers() if ast_after_direct_substitutions else set()
        actual_free_vars_for_show = set()
        
        # Scope for checking freeness: includes program vars and explicit 'show' substitutions
        scope_for_freeness_check = SymbolTable(parent=symbol_table)
        for var_name, val in substitutions_map.items():
            scope_for_freeness_check.create_var(var_name, "int", val) # Add substitutions

        for var_name in potential_free_vars_in_final_ast:
            try:
                value, _type = scope_for_freeness_check.get_var(var_name) # Check in combined scope
                if value is UNASSIGNED: # <<< POINT 5 (Free Var Counting)
                    actual_free_vars_for_show.add(var_name)
                elif _type == "eq": # An 'eq' variable is symbolic unless its content is fully resolved elsewhere
                    # To be truly free, its *content* must contain free vars after considering this scope
                    # For simplicity now, if it's an 'eq' type, and not substituted away, treat its name as a placeholder
                    # A deeper check would be: ast_content = value; if ast_content.collect_identifiers() - scope_for_freeness_check.symbols.keys(): actual_free_vars_for_show.add(var_name)
                    # For now, if it's an 'eq' type variable itself, it's symbolic.
                     actual_free_vars_for_show.add(var_name) # This might overcount if eq var is fully concrete
            except KeyError: # Not in substitutions and not in main symbol_table -> truly free
                actual_free_vars_for_show.add(var_name)
        
        num_free_vars = len(actual_free_vars_for_show)
        output_string = ""
        
        if num_free_vars > 2:
            raise KhwarizmiRuntimeError("Too many free variables for show(). Please provide more substitutions to reduce to 2D or 1D.")
        elif num_free_vars == 0:
            # If the original effective_ast_to_display was a comparison (e.g., show(myEq == 0, x=1, y=2))
            # then evaluate this fully substituted boolean expression.
            # The ast_after_direct_substitutions should now be fully concrete.
            if isinstance(effective_ast_to_display, BinOpNode) and \
               effective_ast_to_display.value in ["==", "!=", "<", ">", "<=", ">="] and \
               ast_after_direct_substitutions is not None:
                
                # Evaluate in a scope that ONLY has the substitutions, not the parent ST,
                # because all variables should have been substituted to get 0 free vars.
                # Or, evaluate in scope_for_freeness_check which has them.
                result_val, result_type = ast_after_direct_substitutions.evaluate(scope_for_freeness_check) # <<< POINT 6
                
                if result_type == "bool":
                    output_string = str(result_val).lower()
                else: 
                    # This means it didn't evaluate to bool, e.g. if it became `5` due to `show(myEq, all_subs)`
                    # where myEq was `x+y`. In this specific case, "Nothing to show" is correct.
                    # The check `isinstance(effective_ast_to_display, BinOpNode)` handles this.
                    output_string = "Nothing to show (expression did not evaluate to bool after substitutions)"
            else: 
                output_string = "Nothing to show"
        else: # num_free_vars == 1 or num_free_vars == 2
            # Stringify using scope_for_freeness_check, which has substitutions + parent link
            equation_str = ast_node_to_string(ast_after_direct_substitutions, scope_for_freeness_check)
            if original_eq_name_for_print:
                output_string = f"{original_eq_name_for_print} = {equation_str}"
            else: 
                output_string = equation_str
        
        print(output_string)
        return None, "void"

class SolveCmdNode(Node): # ... (Assume SolveCmdNode is as in khwarizmi_ops_py_v9_solvecmd) ...
    def evaluate(self, symbol_table: SymbolTable):
        arg_list_node = self.children[0]
        if len(arg_list_node.children) < 2: raise KhwarizmiRuntimeError("solve() needs at least: solve(eqName == int_val, solveForVar).")
        eq_comparison_node = arg_list_node.children[0]
        if not (isinstance(eq_comparison_node, BinOpNode) and eq_comparison_node.value == "=="): raise KhwarizmiRuntimeError("First arg to solve() must be eqName == int_val.")
        eq_var_node = eq_comparison_node.children[0] 
        target_value_node = eq_comparison_node.children[1] 
        if not isinstance(eq_var_node, IdentifierNode): raise KhwarizmiRuntimeError("LHS of eq comparison in solve() must be an eq variable.")
        equation_ast_from_st, eq_type = symbol_table.get_var(eq_var_node.value)
        if eq_type != "eq" or not isinstance(equation_ast_from_st, Node): raise KhwarizmiRuntimeError(f"'{eq_var_node.value}' is not a valid equation variable.")
        target_value, target_type = target_value_node.evaluate(symbol_table)
        if target_type != "int": raise KhwarizmiRuntimeError("RHS of eq comparison in solve() must be an integer.")
        var_to_solve_for_node = arg_list_node.children[1]
        if not isinstance(var_to_solve_for_node, IdentifierNode): raise KhwarizmiRuntimeError("Second arg to solve() must be the variable name.")
        solve_for_var_name = var_to_solve_for_node.value
        substitutions_for_solve: Dict[str, int] = {} 
        for subst_arg_node in arg_list_node.children[2:]:
            if isinstance(subst_arg_node, BinOpNode) and subst_arg_node.value == "==" and isinstance(subst_arg_node.children[0], IdentifierNode):
                var_name = subst_arg_node.children[0].value; val_node = subst_arg_node.children[1]
                sub_val, sub_val_type = val_node.evaluate(symbol_table) 
                if sub_val_type != "int": raise KhwarizmiRuntimeError(f"Substitution for '{var_name}' in solve() must be int, got {sub_val_type}.")
                substitutions_for_solve[var_name] = sub_val
            else: raise KhwarizmiRuntimeError("Invalid substitution in solve(): Expected 'IDENTIFIER == integer_value_or_int_var'.")
        effective_equation_ast = BinOpNode("-", [equation_ast_from_st, IntLiteralNode(target_value)])
        substituted_eq_ast = substitute_ast(effective_equation_ast, substitutions_for_solve, symbol_table)
        if substituted_eq_ast is None: print("Error: Equation became null after substitution during solve."); return None, "void"
        eval_scope_for_terms = SymbolTable(parent=symbol_table) 
        for var, val in substitutions_for_solve.items(): 
            if eval_scope_for_terms.is_declared_locally(var): eval_scope_for_terms.set_var(var, (val, "int"))
            else: eval_scope_for_terms.create_var(var, "int", val)
        try:
            analysis_result = collect_terms_linear(substituted_eq_ast, solve_for_var_name, eval_scope_for_terms)
        except KhwarizmiRuntimeError as e: print(f"Error during symbolic analysis for solve: {e}"); return None, "void"
        except ZeroDivisionError as e: print(f"Error: {e}"); return None, "void"
        if not analysis_result.is_linear: print(f"Error: Equation is not linear with respect to '{solve_for_var_name}' after substitutions."); return None, "void"
        analysis_result.other_free_vars.discard(solve_for_var_name) 
        if analysis_result.other_free_vars: print(f"Error: Cannot solve. Equation has other unresolved symbolic variables: {analysis_result.other_free_vars}."); return None, "void"
        coeff = analysis_result.coeff_sum; const = analysis_result.const_sum
        if coeff == 0:
            if const == 0: print("Infinite solutions")
            else: print("No solution")
        else:
            if (-const % coeff) != 0: print(f"No integer solution for {solve_for_var_name} (result is {-const}/{coeff}).")
            else: solution = -const // coeff; print(f"{solve_for_var_name} = {solution}")
        return None, "void"

class IfNode(Node):
    def __init__(self, condition: Node, if_block: BlockNode, elif_clauses: List[Any] = None, else_block: Optional[BlockNode] = None):
        super().__init__(value="if"); self.condition = condition; self.if_block = if_block
        self.elif_clauses = elif_clauses if elif_clauses else []; self.else_block = else_block
        self.children = [self.condition, self.if_block] + self.elif_clauses + ([self.else_block] if self.else_block else [])
    def evaluate(self, symbol_table: SymbolTable):
        cond_val, cond_type = self.condition.evaluate(symbol_table)
        if cond_type != "bool": raise KhwarizmiRuntimeError("If condition must be boolean.")
        executed_block = False
        if cond_val:
            if_scope = SymbolTable(parent=symbol_table); self.if_block.evaluate(if_scope); executed_block = True
        else:
            for elif_node in self.elif_clauses:
                elif_cond_val, elif_cond_type = elif_node.condition.evaluate(symbol_table) 
                if elif_cond_type != "bool": raise KhwarizmiRuntimeError("Elif condition must be boolean.")
                if elif_cond_val:
                    actual_elif_scope = SymbolTable(parent=symbol_table); elif_node.block.evaluate(actual_elif_scope)
                    executed_block = True; break
            if not executed_block and self.else_block:
                else_scope = SymbolTable(parent=symbol_table); self.else_block.evaluate(else_scope)
        return None, "void"

class ElifNode(Node):
    def __init__(self, condition: Node, block: BlockNode):
        super().__init__(value="elif"); self.condition = condition; self.block = block
        self.children = [self.condition, self.block]

class WhileNode(Node): 
    def evaluate(self, symbol_table: SymbolTable):
        while True:
            cond_val, cond_type = self.children[0].evaluate(symbol_table)
            if cond_type != "bool": raise KhwarizmiRuntimeError("While condition must be boolean.")
            if not cond_val: break
            while_block_scope = SymbolTable(parent=symbol_table); self.children[1].evaluate(while_block_scope)
        return None, "void"