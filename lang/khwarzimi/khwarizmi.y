
%{
#include <stdio.h>
#include <stdlib.h>

int yylex(void);
void yyerror(const char *s) {
    fprintf(stderr, "Erro sintático: %s\n", s);
}
%}

/* Tipos de valor */
%union {
    int ival;
    int bval;
    char* sval;
}

/* Tokens */
%token <ival> T_INT_LITERAL
%token <bval> T_BOOL_LITERAL
%token <sval> T_IDENTIFIER

%token T_BEGIN T_END T_NEWLINE
%token T_INT T_BOOL T_EQTYPE
%token T_IF T_ELIF T_ELSE T_WHILE
%token T_PRINT T_SHOW T_SOLVE T_INPUT

%token T_ASSIGN
%token T_EQ T_NEQ T_LT T_GT T_LTE T_GTE
%token T_AND T_OR
%token '+' '-' '*' '/'

%token '(' ')'

%token T_ERROR

/* Tipos para não-terminais */
%type <ival> expressao
%type <ival> argumentos

/* Precedência */
%left T_OR
%left T_AND
%left T_EQ T_NEQ
%left T_LT T_LTE T_GT T_GTE
%left '+' '-'
%left '*' '/'
%right UMINUS

%start programa

%%

programa:
    lista_declaracoes
;

lista_declaracoes:
    /* vazio */
  | lista_declaracoes declaracao
;

declaracao:
    T_NEWLINE
  | T_INT T_IDENTIFIER T_NEWLINE
  | T_BOOL T_IDENTIFIER T_NEWLINE
  | T_EQTYPE T_IDENTIFIER T_NEWLINE
  | T_INT T_IDENTIFIER T_ASSIGN expressao T_NEWLINE
  | T_BOOL T_IDENTIFIER T_ASSIGN expressao T_NEWLINE
  | T_EQTYPE T_IDENTIFIER T_ASSIGN expressao T_NEWLINE
  | T_IDENTIFIER T_ASSIGN expressao T_NEWLINE
  | T_PRINT '(' expressao ')' T_NEWLINE
  | T_SHOW '(' argumentos ')' T_NEWLINE
  | T_SOLVE '(' argumentos ')' T_NEWLINE
  | if_stmt
  | while_stmt
  | bloco
;

bloco:
    T_BEGIN T_NEWLINE lista_declaracoes T_END T_NEWLINE
;

if_stmt:
    T_IF expressao T_NEWLINE bloco elifs else_opt
;

elifs:
    /* vazio */
  | elifs T_ELIF expressao T_NEWLINE bloco
;

else_opt:
    /* vazio */
  | T_ELSE T_NEWLINE bloco
;

while_stmt:
    T_WHILE expressao T_NEWLINE bloco
;

argumentos:
    expressao
  | argumentos ',' expressao
;

expressao:
    T_INT_LITERAL                     { $$ = $1; }
  | T_BOOL_LITERAL                    { $$ = $1; }
  | T_IDENTIFIER                      { $$ = 0; } // placeholder simbólico
  | T_INPUT '(' ')'                   { $$ = 0; }
  | '(' expressao ')'                { $$ = $2; }
  | expressao '+' expressao          { $$ = $1 + $3; }
  | expressao '-' expressao          { $$ = $1 - $3; }
  | expressao '*' expressao          { $$ = $1 * $3; }
  | expressao '/' expressao          { $$ = $1 / $3; }
  | expressao T_EQ expressao         { $$ = $1 == $3; }
  | expressao T_NEQ expressao        { $$ = $1 != $3; }
  | expressao T_LT expressao         { $$ = $1 < $3; }
  | expressao T_GT expressao         { $$ = $1 > $3; }
  | expressao T_LTE expressao        { $$ = $1 <= $3; }
  | expressao T_GTE expressao        { $$ = $1 >= $3; }
  | expressao T_AND expressao        { $$ = $1 && $3; }
  | expressao T_OR expressao         { $$ = $1 || $3; }
  | '-' expressao %prec UMINUS       { $$ = -$2; }
;

%%

int main() {
    printf("Iniciando parsing da linguagem Khwarizmi...\n");
    return yyparse();
}
