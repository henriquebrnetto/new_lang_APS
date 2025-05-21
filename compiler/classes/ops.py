from classes.node import Node 
from classes.symbol_table import SymbolTable 
from typing import List, Any, Tuple 


class KhwarizmiRuntimeError(Exception):
    pass

class ProgramNode(Node):
    """ Represents the entire program: BEGIN ... END """
    
    def evaluate(self, symbol_table: SymbolTable):
        try:
            return self.children[0].evaluate(symbol_table) 
        except KhwarizmiRuntimeError as e:
            print(f"Runtime Error: {e}")
        except KeyError as e: 
            print(f"Runtime Error (NameError): Variable '{e.args[0]}' not found.") 
        except TypeError as e:
            print(f"Runtime Error (TypeError): {e}")
        except ZeroDivisionError:
            print("Runtime Error: Division by zero.")
        

class BlockNode(Node):
    """ Represents a BEGIN ... END block or a block for if/while """
    
    def evaluate(self, symbol_table: SymbolTable):
        last_stmt_val = (None, "void") 
        for stmt_node in self.children:
            stmt_node.evaluate(symbol_table) 
        return last_stmt_val

class TypeNode(Node):
    """ Represents a type keyword like 'int', 'bool', 'eq' """
    def evaluate(self, symbol_table: SymbolTable):
        return self.value

class VarDecNode(Node):
    """ Variable Declaration: type IDENTIFIER [= expression] """
    def __init__(self, type_name_str: str, var_name: str, init_expression: Node = None):
        super().__init__(value=var_name)
        self.type_name_str = type_name_str
        self.var_name = var_name
        self.init_expression = init_expression
        self.children = [self.init_expression] if self.init_expression else []

    def evaluate(self, symbol_table: SymbolTable):
        if self.type_name_str == "eq":
            if self.init_expression:
                
                symbol_table.create_var(self.var_name, self.type_name_str, self.init_expression)
            else:
                symbol_table.create_var(self.var_name, self.type_name_str, None)
        elif self.init_expression:
            init_val, init_type = self.init_expression.evaluate(symbol_table)
            
            if self.type_name_str == "int" and init_type != "int":
                raise KhwarizmiRuntimeError(f"Type mismatch for variable '{self.var_name}'. Expected 'int', got '{init_type}'.")
            if self.type_name_str == "bool" and init_type != "bool":
                raise KhwarizmiRuntimeError(f"Type mismatch for variable '{self.var_name}'. Expected 'bool', got '{init_type}'.")
            symbol_table.create_var(self.var_name, self.type_name_str, init_val)
        else:
            symbol_table.create_var(self.var_name, self.type_name_str) 
        return None, "void"

class AssignmentNode(Node):
    """ Assignment: IDENTIFIER = expression """
    def evaluate(self, symbol_table: SymbolTable):
        var_name = self.children[0].value
        _ , declared_type = symbol_table.get_var(var_name)

        if declared_type == "eq":
            new_equation_ast = self.children[1] 
            symbol_table.set_var(var_name, (new_equation_ast, "eq"))
            return new_equation_ast, "eq_repr" 
        else:
            new_value, new_type = self.children[1].evaluate(symbol_table)
            if declared_type == "int" and new_type != "int":
                raise KhwarizmiRuntimeError(f"Type mismatch assigning to '{var_name}'. Expected 'int', got '{new_type}'.")
            if declared_type == "bool" and new_type != "bool":
                raise KhwarizmiRuntimeError(f"Type mismatch assigning to '{var_name}'. Expected 'bool', got '{new_type}'.")
            symbol_table.set_var(var_name, (new_value, declared_type))
            return new_value, declared_type

class BinOpNode(Node):
    def evaluate(self, symbol_table: SymbolTable) -> Tuple[Any, str]:
        left_child = self.children[0]
        right_child = self.children[1]

        try:
            left_val, left_type = left_child.evaluate(symbol_table)
            right_val, right_type = right_child.evaluate(symbol_table)

            op = self.value
            if op in ['+', '-', '*', '/']:
                if not (left_type == "int" and right_type == "int"):
                    if left_type == "eq_repr" or right_type == "eq_repr":
                        return self, "eq_repr" 
                    raise KhwarizmiRuntimeError(f"Arithmetic operation '{op}' requires 'int' operands, got '{left_type}' and '{right_type}'.")
                if op == '+': return left_val + right_val, "int"
                if op == '-': return left_val - right_val, "int"
                if op == '*': return left_val * right_val, "int"
                if op == '/':
                    if right_val == 0: raise ZeroDivisionError("Division by zero in Khwarizmi expression.")
                    return left_val // right_val, "int"

            elif op in ["&&", "||"]:
                if not (left_type == "bool" and right_type == "bool"):
                    if left_type == "eq_repr" or right_type == "eq_repr": 
                        return self, "eq_repr"
                    raise KhwarizmiRuntimeError(f"Logical operation '{op}' requires 'bool' operands, got '{left_type}' and '{right_type}'.")
                if op == '&&': return left_val and right_val, "bool"
                if op == '||': return left_val or right_val, "bool"
            
            elif op in ["==", "!=", "<", ">", "<=", ">="]:
                
                can_compare = (left_type == "int" and right_type == "int") or \
                              (left_type == "bool" and right_type == "bool" and op in ["==", "!="])
                
                if not can_compare:
                    if left_type == "eq_repr" or right_type == "eq_repr": 
                         return self, "eq_repr" 
                    raise KhwarizmiRuntimeError(f"Comparison '{op}' requires compatible operands (int/int or bool/bool for ==,!=), got '{left_type}' and '{right_type}'.")
                
                if op == '==': return left_val == right_val, "bool"
                if op == '!=': return left_val != right_val, "bool"
                if op == '<': return left_val < right_val, "bool"
                if op == '>': return left_val > right_val, "bool"
                if op == '<=': return left_val <= right_val, "bool"
                if op == '>=': return left_val >= right_val, "bool"
            else:
                raise KhwarizmiRuntimeError(f"Unknown binary operator: {op}")

        except KeyError: 
            return self, "eq_repr"


class UnOpNode(Node):
    def evaluate(self, symbol_table: SymbolTable) -> Tuple[Any, str]:
        operand_child = self.children[0]
        op = self.value
        try:
            val, type_str = operand_child.evaluate(symbol_table)
            if op == '-':
                if type_str != "int":
                    if type_str == "eq_repr": 
                        return self, "eq_repr"
                    raise KhwarizmiRuntimeError(f"Unary minus requires 'int' operand, got '{type_str}'.")
                return -val, "int"
            else:
                raise KhwarizmiRuntimeError(f"Unknown unary operator: {op}")
        except KeyError: 
            return self, "eq_repr"


class IntLiteralNode(Node):
    def evaluate(self, symbol_table: SymbolTable):
        return self.value, "int"

class BoolLiteralNode(Node):
    def evaluate(self, symbol_table: SymbolTable):
        return self.value, "bool"

class IdentifierNode(Node):
    def evaluate(self, symbol_table: SymbolTable):
        try:
            value, type_str = symbol_table.get_var(self.value) 
            if type_str == "eq": 
                return value, "eq_repr" 
            return value, type_str
        except KeyError:
            return self, "eq_repr" 

class InputNode(Node):
    def evaluate(self, symbol_table: SymbolTable):
        while True:
            try:
                val_str = input() 
                return int(val_str), "int"
            except ValueError:
                print("Invalid input. Please enter an integer.")
            except EOFError:
                raise KhwarizmiRuntimeError("EOF reached while expecting input.")


class EquationNode(Node): 
    def __init__(self, symbolic_expression_node: Node):
        super().__init__(value="equation_wrapper") 
        self.symbolic_expression = symbolic_expression_node
        self.children = [symbolic_expression_node]

    def evaluate(self, symbol_table: SymbolTable):
        return self.symbolic_expression, "eq_repr"

    def get_symbolic_expr(self) -> Node:
        return self.symbolic_expression


class ArgumentListNode(Node):
    def evaluate(self, symbol_table: SymbolTable) -> List[Tuple[Any, str]]:
        evaluated_args = []
        for arg_node in self.children:
            val, type_str = arg_node.evaluate(symbol_table) 
            evaluated_args.append((val, type_str))
        return evaluated_args

class PrintCmdNode(Node):
    def evaluate(self, symbol_table: SymbolTable):
        arg_list_node = self.children[0]
        evaluated_args = arg_list_node.evaluate(symbol_table)
        
        print_values = []
        for val, type_str in evaluated_args:
            if type_str == "bool":
                print_values.append(str(val).lower())
            elif type_str == "eq_repr": 
                print_values.append(f"<SymbolicExpr: {ast_node_to_string(val, symbol_table)} >")
            else:
                print_values.append(str(val))
        print(" ".join(print_values))
        return None, "void"

def ast_node_to_string(node: Any, symbol_table: SymbolTable) -> str:
    """ Helper to convert an AST node (especially symbolic ones) to a string. """
    if not isinstance(node, Node): 
        if isinstance(node, bool): return str(node).lower()
        return str(node)

    if isinstance(node, IdentifierNode):
        try:
            
            value, type_str = symbol_table.get_var(node.value)
            if type_str == "eq_repr": 
                return ast_node_to_string(value, symbol_table) 
            elif type_str == "bool":
                return str(value).lower()
            return str(value) 
        except KeyError:
            return node.value 
    elif isinstance(node, IntLiteralNode):
        return str(node.value)
    elif isinstance(node, BoolLiteralNode):
        return str(node.value).lower()
    elif isinstance(node, BinOpNode):
        left_str = ast_node_to_string(node.children[0], symbol_table)
        right_str = ast_node_to_string(node.children[1], symbol_table)
        return f"({left_str} {node.value} {right_str})"
    elif isinstance(node, UnOpNode):
        operand_str = ast_node_to_string(node.children[0], symbol_table)
        if node.value == '-' and isinstance(node.children[0], (IntLiteralNode)):
             return f"{node.value}{operand_str}"
        
        if node.value == '-' and isinstance(node.children[0], IdentifierNode):
            try:
                val, _ = symbol_table.get_var(node.children[0].value)
                if isinstance(val, (int, float)) and val < 0: 
                     return f"(-({operand_str}))" 
            except KeyError: pass 
            return f"{node.value}{operand_str}"

        return f"({node.value} {operand_str})"
    elif isinstance(node, EquationNode): 
        return ast_node_to_string(node.symbolic_expression, symbol_table)
    else:
        
        return f"<AST:{type(node).__name__}:{node.value}>"


class ShowCmdNode(Node):
    def evaluate(self, symbol_table: SymbolTable):
        arg_list_node = self.children[0]

        if not arg_list_node.children:
            raise KhwarizmiRuntimeError("show() command requires at least one argument (the equation name or expression).")

        first_arg_node = arg_list_node.children[0]
        
        
        equation_ast_to_display = None
        base_display_scope = symbol_table 

        if isinstance(first_arg_node, IdentifierNode):
            eq_name = first_arg_node.value
            stored_ast, eq_type = base_display_scope.get_var(eq_name)
            if eq_type != "eq":
                raise KhwarizmiRuntimeError(f"Variable '{eq_name}' for show() is not an equation (type '{eq_type}').")
            if not isinstance(stored_ast, Node):
                 raise KhwarizmiRuntimeError(f"Equation variable '{eq_name}' does not hold a valid equation structure.")
            equation_ast_to_display = stored_ast
            eq_name_for_print = eq_name
        elif isinstance(first_arg_node, BinOpNode) and first_arg_node.value == "==":
            
            
            equation_ast_to_display = first_arg_node 
            eq_name_for_print = "Equation" 
        else:
            
            equation_ast_to_display = first_arg_node
            eq_name_for_print = "Expression"
        substitutions = {} 
        display_scope = SymbolTable(parent=symbol_table) 

        for subst_arg_node in arg_list_node.children[1:]:
            if isinstance(subst_arg_node, BinOpNode) and subst_arg_node.value == "==" and \
               isinstance(subst_arg_node.children[0], IdentifierNode):
                
                var_to_sub_name = subst_arg_node.children[0].value
                val_expr_node = subst_arg_node.children[1]
                
                sub_val, sub_type = val_expr_node.evaluate(symbol_table) 
                substitutions[var_to_sub_name] = sub_val
                
                
                
                actual_sub_type = "int" if isinstance(sub_val, int) else \
                                  "bool" if isinstance(sub_val, bool) else \
                                  "unknown" 
                display_scope.create_var(var_to_sub_name, actual_sub_type, sub_val)
            else:
                raise KhwarizmiRuntimeError("Invalid substitution format in show(). Expected 'variable == value'.")
        
        
        final_display_scope = display_scope if substitutions else symbol_table
        
        equation_str = ast_node_to_string(equation_ast_to_display, final_display_scope)
        
        if isinstance(first_arg_node, IdentifierNode): 
            print(f"{eq_name_for_print} = {equation_str}")
        else: 
            print(f"{equation_str}") 

        return None, "void"

class SolveCmdNode(Node):
    def evaluate(self, symbol_table: SymbolTable):
        arg_list_node = self.children[0]
        if len(arg_list_node.children) < 2:
            raise KhwarizmiRuntimeError("solve() requires at least two arguments: solve(equation_comparison, variable_to_solve_for, [substitutions...]).")

        eq_comparison_node = arg_list_node.children[0]
        if not (isinstance(eq_comparison_node, BinOpNode) and eq_comparison_node.value == "=="):
            raise KhwarizmiRuntimeError("First argument to solve() must be an equation comparison (e.g., myEq == 0).")

        eq_var_node = eq_comparison_node.children[0] 
        target_value_node = eq_comparison_node.children[1] 

        if not isinstance(eq_var_node, IdentifierNode):
            raise KhwarizmiRuntimeError("LHS of equation comparison in solve() must be an equation variable.")

        
        equation_ast, eq_type = symbol_table.get_var(eq_var_node.value)
        if eq_type != "eq" or not isinstance(equation_ast, Node):
            raise KhwarizmiRuntimeError(f"'{eq_var_node.value}' is not a valid equation for solve().")

        target_value, target_type = target_value_node.evaluate(symbol_table)
        if target_type != "int": 
            raise KhwarizmiRuntimeError("RHS of equation comparison in solve() must evaluate to an integer.")

        var_to_solve_for_node = arg_list_node.children[1]
        if not isinstance(var_to_solve_for_node, IdentifierNode):
            raise KhwarizmiRuntimeError("Second argument to solve() must be the variable name to solve for.")
        solve_for_var_name = var_to_solve_for_node.value

        substitutions = {} 
        for subst_arg_node in arg_list_node.children[2:]:
            if isinstance(subst_arg_node, BinOpNode) and subst_arg_node.value == "==" and \
               isinstance(subst_arg_node.children[0], IdentifierNode):
                var_name = subst_arg_node.children[0].value
                val_node = subst_arg_node.children[1]
                sub_val, _ = val_node.evaluate(symbol_table) 
                substitutions[var_name] = sub_val
            else:
                raise KhwarizmiRuntimeError("Invalid substitution format in solve(). Expected 'variable == value'.")
        
        substituted_eq_str = ast_node_to_string(equation_ast, symbol_table) 
        print(f"Attempting to solve: {substituted_eq_str} == {target_value} for {solve_for_var_name} with substitutions: {substitutions}")
        print(f"Solution for {solve_for_var_name}: <Symbolic solving not yet implemented>")
        
        return None, "void"

class IfNode(Node):
    def __init__(self, condition: Node, if_block: BlockNode, elif_clauses: List[Any] = None, else_block: BlockNode = None):
        super().__init__(value="if")
        self.condition = condition
        self.if_block = if_block
        self.elif_clauses = elif_clauses if elif_clauses else []
        self.else_block = else_block
        self.children = [self.condition, self.if_block] + self.elif_clauses + ([self.else_block] if self.else_block else [])

    def evaluate(self, symbol_table: SymbolTable):
        cond_val, cond_type = self.condition.evaluate(symbol_table)
        if cond_type != "bool": raise KhwarizmiRuntimeError("If condition must be boolean.")
        
        executed_block = False
        if cond_val:
            if_scope = SymbolTable(parent=symbol_table)
            self.if_block.evaluate(if_scope)
            executed_block = True
        else:
            for elif_node in self.elif_clauses:
                elif_cond_val, elif_cond_type = elif_node.condition.evaluate(symbol_table) 
                if elif_cond_type != "bool": raise KhwarizmiRuntimeError("Elif condition must be boolean.")
                if elif_cond_val:
                    elif_scope = SymbolTable(parent=symbol_table)
                    elif_node.block.evaluate(elif_scope)
                    executed_block = True
                    break
            if not executed_block and self.else_block:
                else_scope = SymbolTable(parent=symbol_table)
                self.else_block.evaluate(else_scope)
        return None, "void"

class ElifNode(Node):
    def __init__(self, condition: Node, block: BlockNode):
        super().__init__(value="elif")
        self.condition = condition
        self.block = block
        self.children = [self.condition, self.block]

class WhileNode(Node):
    def evaluate(self, symbol_table: SymbolTable):
        while True:
            cond_val, cond_type = self.children[0].evaluate(symbol_table)
            if cond_type != "bool": raise KhwarizmiRuntimeError("While condition must be boolean.")
            if not cond_val: break
            
            while_block_scope = SymbolTable(parent=symbol_table)
            self.children[1].evaluate(while_block_scope)
        return None, "void"