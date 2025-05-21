%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "khwarizmi.tab.h"

extern YYSTYPE yylval;
%}

DIGITO      [0-9]
LETRA       [a-zA-Z_]
ID          {LETRA}({LETRA}|{DIGITO})*
NUMERO      {DIGITO}+

%option noyywrap
%option yylineno

%%

[ \t\r]+             { /* ignora espaços e tabs */ }
"//".*               { /* ignora comentário de linha */ }
"\n"                { return T_NEWLINE; }

"BEGIN"              { return T_BEGIN; }
"END"                { return T_END; }
"int"                { return T_INT; }
"bool"               { return T_BOOL; }
"eq"                 { return T_EQTYPE; }

"true"               { yylval.bval = 1; return T_BOOL_LITERAL; }
"false"              { yylval.bval = 0; return T_BOOL_LITERAL; }

"if"                 { return T_IF; }
"elif"               { return T_ELIF; }
"else"               { return T_ELSE; }
"while"              { return T_WHILE; }

"print"              { return T_PRINT; }
"show"               { return T_SHOW; }
"solve"              { return T_SOLVE; }
"input"              { return T_INPUT; }

"=="                 { return T_EQ; }
"!="                 { return T_NEQ; }
"<="                 { return T_LTE; }
">="                 { return T_GTE; }
"&&"                 { return T_AND; }
"||"                 { return T_OR; }
"<"                  { return T_LT; }
">"                  { return T_GT; }
"="                  { return T_ASSIGN; }

"("                  { return '('; }
")"                  { return ')'; }
"+"                  { return '+'; }
"-"                  { return '-'; }
"*"                  { return '*'; }
"/"                  { return '/'; }

","                  { return ','; }

{NUMERO}             { yylval.ival = atoi(yytext); return T_INT_LITERAL; }

{ID}                 { yylval.sval = strdup(yytext); return T_IDENTIFIER; }

.                    { fprintf(stderr, "Caractere inesperado na linha %d: '%s'\n", yylineno, yytext); return T_ERROR; }

%%