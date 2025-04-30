/* A Bison parser, made by GNU Bison 3.8.2.  */

/* Bison interface for Yacc-like parsers in C

   Copyright (C) 1984, 1989-1990, 2000-2015, 2018-2021 Free Software Foundation,
   Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* DO NOT RELY ON FEATURES THAT ARE NOT DOCUMENTED in the manual,
   especially those whose name start with YY_ or yy_.  They are
   private implementation details that can be changed or removed.  */

#ifndef YY_YY_KHWARIZMI_TAB_H_INCLUDED
# define YY_YY_KHWARIZMI_TAB_H_INCLUDED
/* Debug traces.  */
#ifndef YYDEBUG
# define YYDEBUG 0
#endif
#if YYDEBUG
extern int yydebug;
#endif

/* Token kinds.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
  enum yytokentype
  {
    YYEMPTY = -2,
    YYEOF = 0,                     /* "end of file"  */
    YYerror = 256,                 /* error  */
    YYUNDEF = 257,                 /* "invalid token"  */
    T_INT_LITERAL = 258,           /* T_INT_LITERAL  */
    T_BOOL_LITERAL = 259,          /* T_BOOL_LITERAL  */
    T_IDENTIFIER = 260,            /* T_IDENTIFIER  */
    T_BEGIN = 261,                 /* T_BEGIN  */
    T_END = 262,                   /* T_END  */
    T_NEWLINE = 263,               /* T_NEWLINE  */
    T_INT = 264,                   /* T_INT  */
    T_BOOL = 265,                  /* T_BOOL  */
    T_EQTYPE = 266,                /* T_EQTYPE  */
    T_IF = 267,                    /* T_IF  */
    T_ELIF = 268,                  /* T_ELIF  */
    T_ELSE = 269,                  /* T_ELSE  */
    T_WHILE = 270,                 /* T_WHILE  */
    T_PRINT = 271,                 /* T_PRINT  */
    T_SHOW = 272,                  /* T_SHOW  */
    T_SOLVE = 273,                 /* T_SOLVE  */
    T_INPUT = 274,                 /* T_INPUT  */
    T_ASSIGN = 275,                /* T_ASSIGN  */
    T_EQ = 276,                    /* T_EQ  */
    T_NEQ = 277,                   /* T_NEQ  */
    T_LT = 278,                    /* T_LT  */
    T_GT = 279,                    /* T_GT  */
    T_LTE = 280,                   /* T_LTE  */
    T_GTE = 281,                   /* T_GTE  */
    T_AND = 282,                   /* T_AND  */
    T_OR = 283,                    /* T_OR  */
    T_ERROR = 284,                 /* T_ERROR  */
    UMINUS = 285                   /* UMINUS  */
  };
  typedef enum yytokentype yytoken_kind_t;
#endif

/* Value type.  */
#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
union YYSTYPE
{
#line 13 "khwarizmi.y"

    int ival;
    int bval;
    char* sval;

#line 100 "khwarizmi.tab.h"

};
typedef union YYSTYPE YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define YYSTYPE_IS_DECLARED 1
#endif


extern YYSTYPE yylval;


int yyparse (void);


#endif /* !YY_YY_KHWARIZMI_TAB_H_INCLUDED  */
