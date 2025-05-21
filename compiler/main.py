from classes.parser import Parser
from classes.symbol_table import SymbolTable
import sys

def main() -> None:

    with open(sys.argv[1]) as f:
        code = f.read()

    symbol_table = SymbolTable()
    try:
        program = Parser.run(code)
        program.evaluate(symbol_table)
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()