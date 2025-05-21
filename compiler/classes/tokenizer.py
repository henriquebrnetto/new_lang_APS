from classes.token_ import Token 

class Tokenizer:
    source: str
    pos: int
    next: Token 

    RESERVED_KEYWORDS = {
        "BEGIN": "BEGIN_KEYWORD",
        "END": "END_KEYWORD",
        "int": "TYPE_INT",
        "bool": "TYPE_BOOL",
        "eq": "TYPE_EQ",
        "if": "IF_KEYWORD",
        "elif": "ELIF_KEYWORD",
        "else": "ELSE_KEYWORD",
        "while": "WHILE_KEYWORD",
        "print": "PRINT_CMD",
        "show": "SHOW_CMD",
        "solve": "SOLVE_CMD",
        "input": "INPUT_CMD", 
        "true": "BOOL_LITERAL", 
        "false": "BOOL_LITERAL", 
    }

    def __init__(self, source: str): 
        self.source = source
        self.pos = 0 
        self.next = None 
        self.select_next() 


    def select_next(self) -> None:
        while self.pos < len(self.source):
            char = self.source[self.pos]

            if char == '\n':
                self.next = Token("NEWLINE", "\n")
                self.pos += 1
                return

            if char.isspace(): 
                self.pos += 1
                continue

            if char == '/' and self.pos + 1 < len(self.source) and self.source[self.pos+1] == '/':
                self.pos += 2 
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self.pos += 1
                continue 
            
            if self.pos + 1 < len(self.source):
                two_char_op = self.source[self.pos : self.pos + 2]
                if two_char_op == "==":
                    self.next = Token("OPERATOR_EQ", "==")
                    self.pos += 2
                    return
                if two_char_op == "!=": # This is NOT EQUAL comparison
                    self.next = Token("OPERATOR_NEQ", "!=")
                    self.pos += 2
                    return
                if two_char_op == "<=":
                    self.next = Token("OPERATOR_LTE", "<=")
                    self.pos += 2
                    return
                if two_char_op == ">=":
                    self.next = Token("OPERATOR_GTE", ">=")
                    self.pos += 2
                    return
                if two_char_op == "&&":
                    self.next = Token("OPERATOR_AND", "&&")
                    self.pos += 2
                    return
                if two_char_op == "||":
                    self.next = Token("OPERATOR_OR", "||")
                    self.pos += 2
                    return

            # Single-character operators and delimiters
            if char == '=': # This is ASSIGNMENT
                self.next = Token("OPERATOR_ASSIGN", "=")
                self.pos += 1
                return
            if char == '!': # <<< NEW: Logical NOT operator
                self.next = Token("OPERATOR_LOGICAL_NOT", "!")
                self.pos += 1
                return
            if char == '<':
                self.next = Token("OPERATOR_LT", "<")
                self.pos += 1
                return
            if char == '>':
                self.next = Token("OPERATOR_GT", ">")
                self.pos += 1
                return
            if char in ['+', '-', '*', '/']:
                op_type = ""
                if char == '+': op_type = "OPERATOR_PLUS"
                elif char == '-': op_type = "OPERATOR_MINUS" # Could be unary or binary
                elif char == '*': op_type = "OPERATOR_MULT"
                elif char == '/': op_type = "OPERATOR_DIV"
                self.next = Token(op_type, char)
                self.pos += 1
                return
            if char == '(':
                self.next = Token("LPAREN", "(")
                self.pos += 1
                return
            if char == ')':
                self.next = Token("RPAREN", ")")
                self.pos += 1
                return
            if char == ',':
                self.next = Token("COMMA", ",")
                self.pos += 1
                return
            
            if char.isdigit():
                num_str = ""
                while self.pos < len(self.source) and self.source[self.pos].isdigit():
                    num_str += self.source[self.pos]
                    self.pos += 1
                self.next = Token("INT_LITERAL", int(num_str))
                return
            
            if char.isalpha() or char == '_': 
                ident_str = ""
                while self.pos < len(self.source) and \
                      (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
                    ident_str += self.source[self.pos]
                    self.pos += 1
                token_type = Tokenizer.RESERVED_KEYWORDS.get(ident_str)
                if token_type:
                    if token_type == "BOOL_LITERAL":
                        self.next = Token(token_type, True if ident_str == "true" else False)
                    else:
                        self.next = Token(token_type, ident_str) 
                else:
                    self.next = Token("IDENTIFIER", ident_str)
                return
            
            raise ValueError(f"Lexical Error: Unexpected character '{char}' at position {self.pos}")

        self.next = Token("EOF", "") 