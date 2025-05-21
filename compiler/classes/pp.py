from classes.tokenizer import Tokenizer
from classes.token_ import Token
from classes.prepro import PrePro
from classes.ops import *

class Parser:
    tokenizer: Tokenizer

    @staticmethod
    def next_is_int():
        return Parser.tokenizer.next.ttype == 'INT'

    @staticmethod
    def next_is_type():
        return Parser.tokenizer.next.ttype in ['I32', 'BOOL', 'STR']

    @staticmethod
    def next_is_rel_exp_operator() -> bool:
        return Parser.tokenizer.next.ttype in ['LESS', 'GREATER', 'EQUALS']

    @staticmethod
    def next_is_exp_operator() -> bool:
        return Parser.tokenizer.next.ttype in ['PLUS', 'MINUS', 'CONCAT']

    @staticmethod
    def next_is_term_operator() -> bool:
        return Parser.tokenizer.next.ttype in ['MULT', 'DIV']

    @staticmethod
    def next_is_eof() -> bool:
        return Parser.tokenizer.next.ttype == 'EOF'

    @staticmethod
    def next_is_par(type_):
        if type_ == 'open' and Parser.tokenizer.next.ttype == 'OPEN_PAR':
            return True
        if type_ == 'close' and Parser.tokenizer.next.ttype == 'CLOSE_PAR':
            return True
        return False

    @staticmethod
    def next_is_bracket(type_):
        if type_ == 'open' and Parser.tokenizer.next.ttype == 'OPEN_BRACKET':
            return True
        if type_ == 'close' and Parser.tokenizer.next.ttype == 'CLOSE_BRACKET':
            return True
        return False

    @staticmethod
    def parse_program():
        tree = Block('BLOCK')
        while not Parser.next_is_eof():
            if Parser.tokenizer.next.ttype == 'FN':
                tree.children.append(Parser.parse_func_declaration())
            else:
                tree.children.append(Parser.parse_statement())
        tree.children.append(FuncCall('main', []))
        return tree

    @staticmethod
    def parse_func_declaration():
        tok = Parser.tokenizer
        if tok.next.ttype != 'FN':
            raise ValueError("Esperado 'fn' para declaração de função")
        tok.select_next()

        if tok.next.ttype != 'IDENTIFIER':
            raise ValueError("Esperado nome da função após 'fn'")
        name = tok.next.value
        tok.select_next()

        if not Parser.next_is_par('open'):
            raise ValueError("Esperado '(' após nome da função")
        tok.select_next()

        params = []
        if not Parser.next_is_par('close'):
            while True:
                if tok.next.ttype != 'IDENTIFIER':
                    raise ValueError("Esperado nome do parâmetro")
                param_name = tok.next.value
                tok.select_next()
                if tok.next.ttype != 'COLON':
                    raise ValueError("Esperado ':' após nome do parâmetro")
                tok.select_next()
                if tok.next.ttype not in ['I32', 'BOOL', 'STR']:
                    raise ValueError("Esperado tipo do parâmetro")
                param_type = tok.next.value
                tok.select_next()
                params.append(VarDec(param_type, [Identifier(param_name)]))
                if tok.next.ttype == 'COMMA':
                    tok.select_next()
                else:
                    break
        if not Parser.next_is_par('close'):
            raise ValueError("Esperado ')' após parâmetros da função")
        tok.select_next()

        if tok.next.ttype not in ['I32', 'BOOL', 'STR', 'VOID']:
            raise ValueError("Esperado tipo de retorno válido após ')'")
        ret_type = tok.next.value
        tok.select_next()

        body = Parser.parse_block()
        return FuncDec(name, ret_type, params, body)

    @staticmethod
    def parse_block():
        tok = Parser.tokenizer
        tree = Block('BLOCK')
        if not Parser.next_is_bracket('open'):
            raise ValueError("Invalid input")
        tok.select_next()
        while not Parser.next_is_bracket('close'):
            if Parser.next_is_eof():
                raise ValueError("Invalid input")
            tree.children.append(Parser.parse_statement())
        tok.select_next()
        return tree

    @staticmethod
    def parse_statement():
        tok = Parser.tokenizer

        if tok.next.ttype == 'OPEN_BRACKET':
            return Parser.parse_block()
        if tok.next.ttype == 'RETURN':
            tok.select_next()
            expr = None
            if tok.next.ttype != 'SEMICOLON':
                expr = Parser.parse_bool_expression()
            if tok.next.ttype != 'SEMICOLON':
                raise ValueError("Esperado ';' após return")
            tok.select_next()
            return Return(expr)

        tree = None
        if tok.next.ttype == 'IDENTIFIER':
            name = tok.next.value
            tok.select_next()
            if tok.next.ttype == 'ASSIGN':
                tok.select_next()
                tree = Assignment('=', [Identifier(name), Parser.parse_bool_expression()])
            elif tok.next.ttype == 'OPEN_PAR':
                tok.select_next()
                args = []
                if tok.next.ttype != 'CLOSE_PAR':
                    args.append(Parser.parse_bool_expression())
                    while tok.next.ttype == 'COMMA':
                        tok.select_next()
                        args.append(Parser.parse_bool_expression())
                if tok.next.ttype != 'CLOSE_PAR':
                    raise ValueError("Invalid input")
                tok.select_next()
                tree = FuncCall(name, args)
            else:
                raise ValueError("Invalid input")

        elif tok.next.ttype == 'PRINTF':
            tok.select_next()
            if not Parser.next_is_par('open'):
                raise ValueError("Invalid input")
            tok.select_next()
            tree = Print('printf', [Parser.parse_bool_expression()])
            if not Parser.next_is_par('close'):
                raise ValueError("Invalid input")
            tok.select_next()

        elif tok.next.ttype == 'VAR':
            tok.select_next()
            if tok.next.ttype != 'IDENTIFIER':
                raise ValueError("Invalid input")
            identifier = Identifier(tok.next.value)
            tok.select_next()
            if tok.next.ttype != 'COLON':
                raise ValueError("Invalid input")
            tok.select_next()
            if not Parser.next_is_type():
                raise ValueError("Invalid input")
            tree = VarDec(tok.next.value, [identifier])
            tok.select_next()
            if tok.next.ttype == 'ASSIGN':
                tok.select_next()
                tree.children.append(Parser.parse_bool_expression())

        elif tok.next.ttype == 'WHILE':
            tok.select_next()
            if not Parser.next_is_par('open'):
                raise ValueError("Invalid input")
            tok.select_next()
            tree = While('while', [Parser.parse_bool_expression()])
            if not Parser.next_is_par('close'):
                raise ValueError("Invalid input")
            tok.select_next()
            tree.children.append(Parser.parse_block())

        elif tok.next.ttype == 'IF':
            tok.select_next()
            if not Parser.next_is_par('open'):
                raise ValueError("Invalid input")
            tok.select_next()
            tree = If('if', [Parser.parse_bool_expression()])
            if not Parser.next_is_par('close'):
                raise ValueError("Invalid input")
            tok.select_next()
            tree.children.append(Parser.parse_block())
            if tok.next.ttype == 'ELSE':
                tok.select_next()
                tree.children.append(Parser.parse_block())

        if tok.next.ttype == 'SEMICOLON':
            if not tree:
                tree = NoOp(';')
            tok.select_next()
        elif isinstance(tree, Node) and type(tree.children[-1]) == Block:
            pass
        else:
            raise ValueError("Invalid input")

        return tree

    @staticmethod
    def parse_bool_expression():
        tok = Parser.tokenizer
        tree = Parser.parse_bool_term()
        while tok.next.ttype == 'OR':
            tok.select_next()
            tree = BinOp('||', [tree, Parser.parse_bool_term()])
        return tree

    @staticmethod
    def parse_bool_term():
        tok = Parser.tokenizer
        tree = Parser.parse_rel_expression()
        while tok.next.ttype == 'AND':
            tok.select_next()
            tree = BinOp('&&', [tree, Parser.parse_rel_expression()])
        return tree

    @staticmethod
    def parse_rel_expression():
        tok = Parser.tokenizer
        tree = Parser.parse_expression()
        while Parser.next_is_rel_exp_operator():
            if tok.next.ttype == 'EQUALS':
                tok.select_next()
                tree = BinOp('==', [tree, Parser.parse_expression()])
            elif tok.next.ttype == 'GREATER':
                tok.select_next()
                tree = BinOp('>', [tree, Parser.parse_expression()])
            elif tok.next.ttype == 'LESS':
                tok.select_next()
                tree = BinOp('<', [tree, Parser.parse_expression()])
        return tree

    @staticmethod
    def parse_expression():
        tok = Parser.tokenizer
        tree = Parser.parse_term()
        while Parser.next_is_exp_operator():
            if tok.next.ttype == 'PLUS':
                tok.select_next()
                tree = BinOp('+', [tree, Parser.parse_term()])
            elif tok.next.ttype == 'MINUS':
                tok.select_next()
                tree = BinOp('-', [tree, Parser.parse_term()])
            elif tok.next.ttype == 'CONCAT':
                tok.select_next()
                tree = BinOp('++', [tree, Parser.parse_term()])
        return tree

    @staticmethod
    def parse_term():
        tok = Parser.tokenizer
        tree = Parser.parse_factor()
        while Parser.next_is_term_operator():
            if tok.next.ttype == 'MULT':
                tok.select_next()
                tree = BinOp('*', [tree, Parser.parse_factor()])
            elif tok.next.ttype == 'DIV':
                tok.select_next()
                tree = BinOp('/', [tree, Parser.parse_factor()])
        return tree

    @staticmethod
    def parse_factor():
        tok = Parser.tokenizer
        if Parser.next_is_int():
            tree = IntVal(tok.next.value)
            tok.select_next()
        elif tok.next.ttype in ['TRUE', 'FALSE']:
            tree = BoolVal(tok.next.value)
            tok.select_next()
        elif tok.next.ttype == 'STRING':
            tree = StrVal(tok.next.value)
            tok.select_next()
        elif tok.next.ttype == 'PLUS':
            tok.select_next()
            tree = UnOp('+', [Parser.parse_factor()])
        elif tok.next.ttype == 'MINUS':
            tok.select_next()
            tree = UnOp('-', [Parser.parse_factor()])
        elif tok.next.ttype == 'NOT':
            tok.select_next()
            tree = UnOp('!', [Parser.parse_factor()])   
        elif Parser.next_is_par('open'):
            tok.select_next()
            tree = Parser.parse_bool_expression()
            if Parser.next_is_par('close'):
                tok.select_next()
            else:
                raise ValueError("Invalid input")
        elif tok.next.ttype == 'IDENTIFIER':
            name = tok.next.value
            tok.select_next()
            if tok.next.ttype == 'OPEN_PAR':
                tok.select_next()
                args = []
                if tok.next.ttype != 'CLOSE_PAR':
                    args.append(Parser.parse_bool_expression())
                    while tok.next.ttype == 'COMMA':
                        tok.select_next()
                        args.append(Parser.parse_bool_expression())
                if tok.next.ttype != 'CLOSE_PAR':
                    raise ValueError("Invalid input")
                tok.select_next()
                tree = FuncCall(name, args)
            else:
                tree = Identifier(name)
        elif tok.next.ttype == 'READER':
            tok.select_next()
            if not Parser.next_is_par('open'):
                raise ValueError("Invalid input")
            tok.select_next()
            if not Parser.next_is_par('close'):
                raise ValueError("Invalid input")
            tok.select_next()
            tree = Reader('reader')
        else:
            raise ValueError("Invalid input")
        return tree

    @staticmethod
    def run(code: str):
        code = PrePro.filter(code)
        Parser.tokenizer = Tokenizer(code, pos=-1, next=Token('', ''))
        Parser.tokenizer.select_next()
        program = Parser.parse_program()
        if Parser.next_is_eof():
            return program
        raise Exception('Something went wrong.')