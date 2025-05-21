from dataclasses import dataclass, field
from classes.token_ import Token
import re

@dataclass
class Tokenizer:
    source: str
    pos: int = -1
    next: Token = field(default_factory=lambda: Token('', ''))

    def __post_init__(self):
        self.__reserved_kw = {
            'int':    'INT',
            'bool':   'BOOL',
            'eq':     'EQ',
            'show':   'SHOW',
            'solve':  'SOLVE',
            'begin':  'BEGIN',
            'end':    'END',
            'elif':   'ELIF',
            'print':  'PRINTF',
            'input':  'READER',
            'true':   'TRUE',
            'false':  'FALSE'
        }

    def check_eof(self) -> bool:
        if self.pos >= len(self.source):
            return True
        return False
    
    def next_is_letter(self, only=False) -> bool:
        if only:
            return True if re.match(r'[A-Za-z]', self.source[self.pos]) else False
        return True if re.match(r'[A-Za-z_]', self.source[self.pos]) else False

    def skip_spaces(self) -> None:
        pos = self.pos
        espaco = False
        try:
            while (re.match(r'\s', self.source[pos])):
                espaco = True
                pos += 1
        except IndexError:
            pass
        finally:
            if espaco:
                pos -= 1
        self.pos = pos

    def select_next(self) -> None:
        self.pos += 1
        if self.pos >= len(self.source):
            self.pos = len(self.source) - 1
            self.next = Token('EOF', '')
            return
        
        token = self.source[self.pos]
        if token == '+':
            if self.source[self.pos + 1] == '+':
                self.pos += 1
                self.next = Token('CONCAT', '++')
            else:
                self.next = Token('PLUS', '+')

        elif token == '-':
            self.next = Token('MINUS', '-')

        elif token == '*':
            self.next = Token('MULT', '*')
        
        elif token == '/':
            self.next = Token('DIV', '/')

        elif token == '(':
            self.next = Token('OPEN_PAR', '(')
        
        elif token == ')':
            self.next = Token('CLOSE_PAR', ')')

        elif token == '{':
            self.next = Token('OPEN_BRACKET', '{')
        
        elif token == '}':
            self.next = Token('CLOSE_BRACKET', '}')

        elif token == ',':
            self.next = Token('COMMA', ',')
        
        elif token == ';':
            self.next = Token('SEMICOLON', ';')

        elif token == '>':
            if self.source[self.pos + 1] == '=':
                self.pos += 1
                self.next = Token('GREATEREQ', '>=')
            else:
                self.next = Token('GREATER', '>')
        
        elif token == '<':
            if self.source[self.pos + 1] == '=':
                self.pos += 1
                self.next = Token('LESSEQ', '<=')
            else:
                self.next = Token('LESS', '<')
        
        elif token == '!':
            if self.source[self.pos + 1] == '=':
                self.pos += 1
                self.next = Token('NOTEQ', '!=')
            else:
                self.next = Token('NOT', '!')

        elif token == ':':
            self.next = Token('COLON', ':')
        
        elif token == '=':
            if self.source[self.pos + 1] == '=':
                self.pos += 1
                self.next = Token('EQUALS', '==')
            else:
                self.next = Token('ASSIGN', '=')
        
        elif token == '&':
            if self.source[self.pos + 1] == '&':
                self.pos += 1
                self.next = Token('AND', '&&')
            else:
                self.next = Token('INVALID', token)

        elif token == '|':
            if self.source[self.pos + 1] == '|':
                self.pos += 1
                self.next = Token('OR', '||')
            else:
                self.next = Token('INVALID', token)
        
        elif token == '"':
            tokens = ''

            self.pos += 1
            token = self.source[self.pos]
            while token != '"' and not self.check_eof():
                tokens += token
                try:
                    self.pos += 1
                    token = self.source[self.pos]
                except IndexError:
                    break

            self.next = Token('STRING', tokens)

        
        elif self.next_is_letter(only=True):
            tokens = ''
            while self.next_is_letter() and not self.check_eof():
                tokens += self.source[self.pos]
                self.pos += 1
            self.pos -= 1

            if tokens in self.__reserved_kw:
                tok_type = self.__reserved_kw[tokens]
            else:
                tok_type = 'IDENTIFIER'

            self.next = Token(tok_type, tokens)


        elif token == ' ':
            self.skip_spaces()
            self.select_next()
        

        elif token == '\n':
            self.skip_spaces()
            self.select_next()


        elif token.isdigit():
            tokens = ''

            while token.isdigit() and not self.check_eof():
                tokens += token
                try:
                    self.pos += 1
                    token = self.source[self.pos]
                except IndexError:
                    break
            self.pos -= 1
            self.next = Token('INT', int(tokens))

        else:
            self.next = Token('INVALID', token)