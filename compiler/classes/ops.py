from classes.node import Node
from classes.symbol_table import SymbolTable
from classes.exceptions import ReturnException
from math import prod


#----------------------------------------------------------------------
# EXPRESSIONS
#----------------------------------------------------------------------

class BinOp(Node):
    def evaluate(self, symbol_table : SymbolTable):

        vals, types = zip(*[child.evaluate(symbol_table) for child in self.children])

        if self.value == '+':
            if types[0] == 'int' and types[1] == 'int':
                return sum(vals), 'int'
            else:
                raise ValueError("Invalid input.")
        
        if self.value == '-':
            if types[0] == 'int' and types[1] == 'int':
                vals = (vals[0], -vals[1])
                return sum(vals), 'int'
            else:
                raise ValueError("Invalid input.")
            
        if self.value == '*':
            if types[0] == 'int' and types[1] == 'int':
                return prod(vals), 'int'
            else:
                raise ValueError("Invalid input.")
            
        
        if self.value == '/':
            if types[0] == 'int' and types[1] == 'int':
                vals = (vals[0], pow(vals[1], -1))
                return round(prod(vals)), 'int'
            else:
                raise ValueError("Invalid input.")
            
        
        if self.value == '&&':
            if types[0] == 'bool' and types[1] == 'bool':
                return vals[0] and vals[1], 'bool'
            else:
                raise ValueError("Invalid input.")

        
        if self.value == '||':
            if types[0] == 'bool' and types[1] == 'bool':
                return vals[0] or vals[1], 'bool'
            else:
                raise ValueError("Invalid input.")
            
            
        if self.value == '==':
            if types[0] != types[1]:
                raise TypeError("Invalid input.")
            return vals[0] == vals[1], 'bool'
            
        
        if self.value == '>':
            if types[0] != types[1]:
                raise TypeError("Invalid input.")
            return vals[0] > vals[1], 'bool'
        

        if self.value == '<':
            if types[0] != types[1]:
                raise TypeError("Invalid input.")
            return vals[0] < vals[1], 'bool'
            
        
        if self.value == '++':

            if types[0] == 'bool':
                vals = (str(vals[0]).lower(), vals[1])

            if types[1] == 'bool':
                vals = (vals[0], str(vals[1]).lower())
            
            return "".join([str(vals[0]), str(vals[1])]), 'str'
        

class UnOp(Node):
    def evaluate(self, symbol_table : SymbolTable):

        val, type_ = self.children[0].evaluate(symbol_table)
        if self.value == '+':
            return val, type_
        if self.value == '-':
            return -val, type_
        if self.value == '!':
            return not val, type_


class IntVal(Node):
    def evaluate(self, symbol_table : SymbolTable):
        return self.value, 'int'
    
class BoolVal(Node):
    def evaluate(self, symbol_table : SymbolTable):
        return self.value, 'bool'
    
class StrVal(Node):
    def evaluate(self, symbol_table : SymbolTable):
        return self.value, 'str'

class Reader(Node):
    def evaluate(self, symbol_table):
        return int(input()), 'int'
    

class Identifier(Node):
    def evaluate(self, symbol_table : SymbolTable):
        return symbol_table.get_var(self.value)
    

class NoOp(Node):
    def evaluate(self, symbol_table : SymbolTable):
        return super().evaluate(symbol_table), 'void'

#----------------------------------------------------------------------
# STATEMENTS
#----------------------------------------------------------------------

class Block(Node):
    def evaluate(self, symbol_table : SymbolTable):
        # cria um escopo filho para este bloco
        local = SymbolTable(parent=symbol_table)
        for node in self.children:
            try:
                node.evaluate(local)
            except ReturnException:
                # propaga o return sem alterar o escopo externo
                raise
    


class Assignment(Node):
    def evaluate(self, symbol_table : SymbolTable):
        symbol_table.set_var(self.children[0].value, self.children[1].evaluate(symbol_table))
    

class  If(Node):
    def evaluate(self, symbol_table : SymbolTable):
        child0 = self.children[0].evaluate(symbol_table)
        if child0[1] != 'bool':
            raise ValueError("Invalid input.")
        if child0[0]:
            self.children[1].evaluate(symbol_table)
        elif len(self.children) == 3:
                self.children[2].evaluate(symbol_table)


class While(Node):
    def evaluate(self, symbol_table : SymbolTable):
        child0 = self.children[0].evaluate(symbol_table)
        if child0[1] != 'bool':
            raise ValueError("Invalid input.")
        while child0[0]:
            self.children[1].evaluate(symbol_table)
            child0 = self.children[0].evaluate(symbol_table)
            if child0[1] != 'bool':
                raise ValueError("Invalid input.")


class Print(Node):
    def evaluate(self, symbol_table : SymbolTable):
        child = self.children[0].evaluate(symbol_table)
        print(child[0] if child[1] != 'bool' else str(child[0]).lower())


class VarDec(Node):
    def evaluate(self, symbol_table : SymbolTable):
        var_name = self.children[0].value
        symbol_table.create_var(var_name, self.value)

        if len(self.children) == 2:
            init_node = self.children[1]
            if isinstance(init_node, Reader):
                init_val, init_type = 0, 'int'
            else:
                init_val, init_type = init_node.evaluate(symbol_table)

            if init_type != self.value:
                print(self)
                raise TypeError(f"Type mismatch for variable '{var_name}'")

            symbol_table.set_var(var_name, (init_val, init_type))


class FuncDec(Node):
   def __init__(self, func_name, return_type, params, body):
       super().__init__(func_name, [])
       self.return_type = return_type
       self.params = params
       self.body = body

   def evaluate(self, symbol_table : SymbolTable):
       symbol_table.create_var(self.value, self.return_type)
       symbol_table.set_var(self.value, (self, self.return_type))
       

class FuncCall(Node):
   def __init__(self, func_name, args):
       super().__init__(func_name, [])
       self.args = args

   def evaluate(self, symbol_table : SymbolTable):
       func_node, func_type = symbol_table.get_var(self.value)
       if not isinstance(func_node, FuncDec):
           raise ValueError(f"'{self.value}' não é uma função.")

       if len(self.args) != len(func_node.params):
           raise ValueError(
               f"Função '{self.value}' esperava {len(func_node.params)} argumentos, mas recebeu {len(self.args)}."
           )

       local = SymbolTable(parent=symbol_table)
       for decl, expr in zip(func_node.params, self.args):
           val, typ = expr.evaluate(symbol_table)
           if typ != decl.value:
               raise TypeError(
                   f"Argumento para '{decl.children[0].value}' esperado '{decl.value}', recebeu '{typ}'."
               )
           local.create_var(decl.children[0].value, decl.value)
           local.set_var(decl.children[0].value, (val, typ))

       try:
           func_node.body.evaluate(local)
       except ReturnException as ret:
           if func_node.return_type == 'void':
               raise ValueError(f"Função '{self.value}' não deveria retornar valor.")
           if ret.type_ != func_node.return_type:
               raise TypeError(
                   f"Função '{self.value}' deveria retornar '{func_node.return_type}', retornou '{ret.type_}'."
               )
           return ret.value, ret.type_

       if func_node.return_type != 'void':
           raise ValueError(f"Função '{self.value}' deveria retornar '{func_node.return_type}'.")
       return 0, 'void'


class Return(Node):
   def __init__(self, expr=None):
       super().__init__('return', [expr] if expr else [])

   def evaluate(self, symbol_table : SymbolTable):
       if not self.children:
           raise ReturnException(0, 'void')
       val, typ = self.children[0].evaluate(symbol_table)
       raise ReturnException(val, typ)
   
class EqDec(Node):
    def __init__(self, name, expr):
        super().__init__(name, [expr])
    def evaluate(self, st):
        # 1) collect free-vars from expr AST
        free = { node.value: st.get_var(node.value)
                 for node in self.children[0].collect_identifiers() }
        free[self.value] = None
        # 2) register in symbol table
        st.create_eq(self.value, self.children[0], free)

class ShowNode(Node):
    def __init__(self, args):
        super().__init__('show', args)
    def evaluate(self, st):
        # stub: later plug in matplotlib
        print(f"<show {self.children}>")

class SolveNode(Node):
    def __init__(self, args):
        super().__init__('solve', args)
    def evaluate(self, st):
        # stub: later call your linear solver
        print(f"<solve {self.children}>")