from classes.tokenizer import Tokenizer
from classes.ops import *
from typing import Any
from classes.node import Node
from classes.prepro import PrePro
import sys

class Parser:
    tokenizer: Tokenizer

    def __init__(self, tokenizer: Tokenizer):
        self.tokenizer = tokenizer
        
        
        self.precedence = {
            "OPERATOR_OR": 1,    
            "OPERATOR_AND": 2,   
            "OPERATOR_EQ": 3,    
            "OPERATOR_NEQ": 3,   
            "OPERATOR_LT": 4,    
            "OPERATOR_GT": 4,    
            "OPERATOR_LTE": 4,   
            "OPERATOR_GTE": 4,   
            "OPERATOR_PLUS": 5,  
            "OPERATOR_MINUS": 5, 
            "OPERATOR_MULT": 6,  
            "OPERATOR_DIV": 6
        }

    def consume(self, expected_type: str, expected_value: Any = None):
        """Consumes the current token if it matches expected_type and optionally expected_value."""
        token = self.tokenizer.next
        if token.ttype == expected_type:
            if expected_value is not None and token.value != expected_value:
                raise SyntaxError(f"Parser Error: Expected token value '{expected_value}' for type '{expected_type}', but got '{token.value}'")
            self.tokenizer.select_next()
            return token
        else:
            raise SyntaxError(f"Parser Error: Expected token type '{expected_type}', but got '{token.ttype}' (value: '{token.value}')")

    def parse_program(self) -> ProgramNode:
        """ Parses the entire Khwarizmi program: BEGIN lista_declaracoes END """
        self.consume("BEGIN_KEYWORD", "BEGIN")
        self.consume_optional_newlines()
        
        
        main_block_node = self.parse_block_content(is_program_root=True)
        
        self.consume("END_KEYWORD", "END")
        self.consume_optional_newlines() 
        self.consume("EOF") 
        return ProgramNode(value="Program", children=[main_block_node])

    def parse_block_content(self, is_program_root: bool = False) -> BlockNode:
        """ Parses the content of a block: a list of declarations until END or an outer block's end. """
        statements = []
        
        
        while self.tokenizer.next.ttype != "END_KEYWORD":
            statements.append(self.parse_declaration_or_statement())
            if self.tokenizer.next.ttype == "NEWLINE":
                 self.consume("NEWLINE")
                 self.consume_optional_newlines() 
            elif self.tokenizer.next.ttype == "END_KEYWORD": 
                break
            elif self.tokenizer.next.ttype == "EOF" and is_program_root: 
                break
            elif self.tokenizer.next.ttype == "EOF" and not is_program_root:
                raise SyntaxError("Parser Error: Unexpected EOF inside a nested block. Missing END?")
            else:                   
                  pass


        return BlockNode(value="Block", children=statements)

    def parse_block(self) -> BlockNode:
        """ Parses a nested block: BEGIN lista_declaracoes END """
        self.consume("BEGIN_KEYWORD", "BEGIN")
        self.consume_optional_newlines()
        block_node = self.parse_block_content()
        self.consume("END_KEYWORD", "END")
        return block_node
        
    def consume_optional_newlines(self):
        """Consumes one or more consecutive NEWLINE tokens."""
        while self.tokenizer.next.ttype == "NEWLINE":
            self.consume("NEWLINE")

    def parse_declaration_or_statement(self) -> Node:
        """ Parses a single declaration or statement. """
        token = self.tokenizer.next
        node = None

        if token.ttype in ["TYPE_INT", "TYPE_BOOL", "TYPE_EQ"]:
            node = self.parse_variable_declaration()
        elif token.ttype == "IDENTIFIER":
            
            node = self.parse_assignment_statement()
        elif token.ttype == "IF_KEYWORD":
            node = self.parse_if_statement()
        elif token.ttype == "WHILE_KEYWORD":
            node = self.parse_while_statement()
        elif token.ttype == "PRINT_CMD":
            node = self.parse_print_command()
        elif token.ttype == "SHOW_CMD":
            node = self.parse_show_command()
        elif token.ttype == "SOLVE_CMD":
            node = self.parse_solve_command()
        elif token.ttype == "NEWLINE": 
            self.consume("NEWLINE") 
            
            return self.parse_declaration_or_statement() 
        else:
            raise SyntaxError(f"Parser Error: Unexpected token at start of statement: {token.ttype} ('{token.value}')")
        
        return node

    def parse_type(self) -> TypeNode:
        token = self.tokenizer.next
        if token.ttype == "TYPE_INT":
            self.consume("TYPE_INT")
            return TypeNode("int")
        elif token.ttype == "TYPE_BOOL":
            self.consume("TYPE_BOOL")
            return TypeNode("bool")
        elif token.ttype == "TYPE_EQ":
            self.consume("TYPE_EQ")
            return TypeNode("eq")
        else:
            raise SyntaxError(f"Parser Error: Expected type (int, bool, eq), got {token.ttype}")

    def parse_variable_declaration(self) -> VarDecNode:
        type_node = self.parse_type()
        identifier_token = self.consume("IDENTIFIER")
        init_expr_node = None
        if self.tokenizer.next.ttype == "OPERATOR_ASSIGN":
            self.consume("OPERATOR_ASSIGN", "=")
            init_expr_node = self.parse_expression()
        
        
        return VarDecNode(type_name_str=type_node.value,
                          var_name=identifier_token.value,
                          init_expression=init_expr_node)

    def parse_assignment_statement(self) -> AssignmentNode:
        identifier_node = IdentifierNode(self.consume("IDENTIFIER").value)
        self.consume("OPERATOR_ASSIGN", "=")
        expr_node = self.parse_expression()
        
        return AssignmentNode(value="=", children=[identifier_node, expr_node])

    def parse_if_statement(self) -> IfNode:
        self.consume("IF_KEYWORD")
        condition_expr = self.parse_expression()
        self.consume_optional_newlines() 
        if_block = self.parse_block()
        
        elif_clauses = []
        while self.tokenizer.next.ttype == "ELIF_KEYWORD":
            self.consume("ELIF_KEYWORD")
            elif_condition_expr = self.parse_expression()
            self.consume_optional_newlines()
            elif_block = self.parse_block()
            elif_clauses.append(ElifNode(condition=elif_condition_expr, block=elif_block))

        else_block_node = None
        if self.tokenizer.next.ttype == "ELSE_KEYWORD":
            self.consume("ELSE_KEYWORD")
            self.consume_optional_newlines()
            else_block_node = self.parse_block()
            
        return IfNode(condition=condition_expr, if_block=if_block,
                      elif_clauses=elif_clauses, else_block=else_block_node)

    def parse_while_statement(self) -> WhileNode:
        self.consume("WHILE_KEYWORD")
        condition_expr = self.parse_expression()
        self.consume_optional_newlines() 
        loop_block = self.parse_block()
        return WhileNode(value="while", children=[condition_expr, loop_block])

    def parse_argument_list(self) -> ArgumentListNode:
        args = []
        if self.tokenizer.next.ttype != "RPAREN": 
            args.append(self.parse_expression())
            while self.tokenizer.next.ttype == "COMMA":
                self.consume("COMMA")
                args.append(self.parse_expression())
        return ArgumentListNode(value="args", children=args)

    def parse_print_command(self) -> PrintCmdNode:
        self.consume("PRINT_CMD")
        self.consume("LPAREN", "(")
        arg_list_node = self.parse_argument_list()
        self.consume("RPAREN", ")")
        return PrintCmdNode(value="print", children=[arg_list_node])

    def parse_show_command(self) -> ShowCmdNode:
        self.consume("SHOW_CMD")
        self.consume("LPAREN", "(")
        arg_list_node = self.parse_argument_list()
        self.consume("RPAREN", ")")
        return ShowCmdNode(value="show", children=[arg_list_node])

    def parse_solve_command(self) -> SolveCmdNode:
        self.consume("SOLVE_CMD")
        self.consume("LPAREN", "(")
        arg_list_node = self.parse_argument_list()
        self.consume("RPAREN", ")")
        return SolveCmdNode(value="solve", children=[arg_list_node])

    
    def parse_expression(self, min_precedence=1) -> Node:
        """ Parses a Khwarizmi expression using precedence climbing. """
        
        lhs = self.parse_factor()

        while True:
            op_token = self.tokenizer.next
            op_type = op_token.ttype

            
            if op_type not in self.precedence or self.precedence[op_type] < min_precedence:
                break

            op_prec = self.precedence[op_type]
            op_val = op_token.value 
            self.consume(op_type) 

            rhs = self.parse_expression(op_prec + 1)
            if hasattr(lhs, 'is_equation_context') and lhs.is_equation_context:
                 
                 lhs = BinOpNode(value=op_val, children=[lhs, rhs]) 
            else:
                 lhs = BinOpNode(value=op_val, children=[lhs, rhs])
        
        return lhs


    def parse_factor(self) -> Node:
        """ Parses the most tightly bound parts of expressions: literals, identifiers, (expr), input, unary ops. """
        token = self.tokenizer.next

        if token.ttype == "OPERATOR_MINUS": 
            self.consume("OPERATOR_MINUS")
            
            
            operand = self.parse_factor() 
            return UnOpNode(value="-", children=[operand])
        
        elif token.ttype == "INT_LITERAL":
            self.consume("INT_LITERAL")
            return IntLiteralNode(token.value)
        elif token.ttype == "BOOL_LITERAL": 
            self.consume("BOOL_LITERAL")
            return BoolLiteralNode(token.value)
        elif token.ttype == "IDENTIFIER":
            self.consume("IDENTIFIER")
            return IdentifierNode(token.value)
        elif token.ttype == "LPAREN":
            self.consume("LPAREN")
            expr_node = self.parse_expression() 
            self.consume("RPAREN")
            return expr_node
        elif token.ttype == "INPUT_CMD": 
            self.consume("INPUT_CMD")
            self.consume("LPAREN")
            self.consume("RPAREN")
            return InputNode("input")
        else:
            raise SyntaxError(f"Parser Error: Unexpected token in factor: {token.ttype} ('{token.value}')")

    @staticmethod
    def run(code: str) -> ProgramNode:

        try:
            processed_code = PrePro.filter(code)
        except Exception as e:
            print(f"Error during preprocessing: {e}")
            sys.exit(1)
        tokenizer = Tokenizer(code)
        parser = Parser(tokenizer)
        program_ast = parser.parse_program()
        
        if parser.tokenizer.next.ttype != "EOF": 
            raise SyntaxError(f"Parser Error: Expected EOF after program, but found {parser.tokenizer.next.ttype}")
            
        return program_ast