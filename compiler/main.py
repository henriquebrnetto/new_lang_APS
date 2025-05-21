import sys
from classes.parser import Parser
from classes.symbol_table import SymbolTable
from classes.ops import ProgramNode

def main() -> None:
    if len(sys.argv) < 2:
        print("Khwarizmi Language Compiler")
        print("Usage: python main.py <filepath.kh>")
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        with open(filepath, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: Source file not found at '{filepath}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{filepath}': {e}")
        sys.exit(1)

    ast_root: ProgramNode
    try:
        ast_root = Parser.run(source_code)
    except SyntaxError as e: 
        print(f"Syntax Error: {e}")
        sys.exit(1)
    except ValueError as e: 
        print(f"Lexical Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during parsing/tokenization: {e}")
        sys.exit(1)
    global_symbol_table = SymbolTable(parent=None) 

    print("\n-- Interpreting (Evaluating) --")
    try:
        ast_root.evaluate(global_symbol_table)
        print("\n-- Execution Finished --")
    except Exception as e: 
        print(f"\n!! RUNTIME ERROR !!")
        print(f"Error Type: {type(e).__name__}")
        print(f"Message: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()