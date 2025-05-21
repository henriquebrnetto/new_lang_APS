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
        return Parser.tokenizer.next.ttype in ['INT', 'BOOL']

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
        tt = Parser.tokenizer.next.ttype
        return (type_ == 'open' and tt == 'OPEN_PAR') or (type_ == 'close' and tt == 'CLOSE_PAR')

    @staticmethod
    def next_is_bracket(type_):
        tt = Parser.tokenizer.next.ttype
        return (type_ == 'open' and tt == 'OPEN_BRACKET') or (type_ == 'close' and tt == 'CLOSE_BRACKET')

    @staticmethod
    def parse_program():
        tree = Block('BLOCK')
        while not Parser.next_is_eof():
            if Parser.tokenizer.next.ttype == 'FN':
                tree.children.append(Parser.parse_func_declaration())
            else:
                tree.children.append(Parser.parse_statement())
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
                if tok.next.ttype not in ['INT', 'BOOL']:
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

        if tok.next.ttype not in ['INT', 'BOOL']:
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

        # —————————————
        # Block
        # —————————————
        if tok.next.ttype == 'OPEN_BRACKET':
            return Parser.parse_block()

        # —————————————
        # Return
        # —————————————
        if tok.next.ttype == 'RETURN':
            tok.select_next()
            expr = None
            if tok.next.ttype != 'SEMICOLON':
                expr = Parser.parse_bool_expression()
            if tok.next.ttype != 'SEMICOLON':
                raise ValueError("Esperado ';' após return")
            tok.select_next()
            return Return(expr)

        # —————————————
        # Typed declarations: int x [= expr]
        # —————————————
        if tok.next.ttype in ('INT', 'BOOL'):
            typ = tok.next.value
            tok.select_next()
            if tok.next.ttype != 'IDENTIFIER':
                raise ValueError("Expected identifier after type")
            name = tok.next.value
            tok.select_next()

            # build the children list: first the variable itself
            children = [Identifier(name)]
            # optional initializer
            if tok.next.ttype == 'ASSIGN':
                tok.select_next()
                children.append(Parser.parse_bool_expression())

            # pass (type, children) → exactly two args
            tree = VarDec(typ, children)
            # consume trailing semicolon if present
            if tok.next.ttype == 'SEMICOLON':
                tok.select_next()
            return tree

        # —————————————
        # Equation declarations: eq fx = expr
        # —————————————
        if tok.next.ttype == 'EQ':
            tok.select_next()
            if tok.next.ttype != 'IDENTIFIER':
                raise ValueError("Expected name after 'eq'")
            name = tok.next.value
            tok.select_next()
            if tok.next.ttype != 'ASSIGN':
                raise ValueError("Expected '=' in equation declaration")
            tok.select_next()
            expr = Parser.parse_bool_expression()
            return EqDec(name, expr)

        # —————————————
        # show(...) plotting
        # —————————————
        if tok.next.ttype == 'SHOW':
            tok.select_next()
            if not Parser.next_is_par('open'):
                raise ValueError("Expected '(' after show")
            tok.select_next()
            args = [Parser.parse_bool_expression()]
            while tok.next.ttype == 'COMMA':
                tok.select_next()
                args.append(Parser.parse_bool_expression())
            if not Parser.next_is_par('close'):
                raise ValueError("Expected ')' after show args")
            tok.select_next()
            return ShowNode(args)

        # —————————————
        # solve(...) solving
        # —————————————
        if tok.next.ttype == 'SOLVE':
            tok.select_next()
            if not Parser.next_is_par('open'):
                raise ValueError("Expected '(' after solve")
            tok.select_next()
            first = Parser.parse_bool_expression()
            args = [first]
            while tok.next.ttype == 'COMMA':
                tok.select_next()
                # bare IDENTIFIER pins a var; otherwise another BoolExpr
                if tok.next.ttype == 'IDENTIFIER' and not Parser.next_is_rel_exp_operator():
                    args.append(Identifier(tok.next.value))
                    tok.select_next()
                else:
                    args.append(Parser.parse_bool_expression())
            if not Parser.next_is_par('close'):
                raise ValueError("Expected ')' after solve args")
            tok.select_next()
            return SolveNode(args)

        # —————————————
        # Assignment or function call
        # —————————————
        if tok.next.ttype == 'IDENTIFIER':
            name = tok.next.value
            tok.select_next()

            # Assignment
            if tok.next.ttype == 'ASSIGN':
                tok.select_next()
                stmt = Assignment('=', [Identifier(name), Parser.parse_bool_expression()])
                if tok.next.ttype == 'SEMICOLON':
                    tok.select_next()
                return stmt

            # Function call
            if tok.next.ttype == 'OPEN_PAR':
                tok.select_next()
                args = []
                if not Parser.next_is_par('close'):
                    args.append(Parser.parse_bool_expression())
                    while tok.next.ttype == 'COMMA':
                        tok.select_next()
                        args.append(Parser.parse_bool_expression())
                if not Parser.next_is_par('close'):
                    raise ValueError("Invalid input")
                tok.select_next()
                stmt = FuncCall(name, args)
                if tok.next.ttype == 'SEMICOLON':
                    tok.select_next()
                return stmt

            raise ValueError("Invalid input")

        # —————————————
        # printf(...)
        # —————————————
        if tok.next.ttype == 'PRINTF':
            tok.select_next()
            if not Parser.next_is_par('open'):
                raise ValueError("Invalid input")
            tok.select_next()
            expr = Parser.parse_bool_expression()
            if not Parser.next_is_par('close'):
                raise ValueError("Invalid input")
            tok.select_next()
            if tok.next.ttype == 'SEMICOLON':
                tok.select_next()
            return Print('printf', [expr])
        
        # —————————————
        # while(...) loop
        # —————————————
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

        # —————————————
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