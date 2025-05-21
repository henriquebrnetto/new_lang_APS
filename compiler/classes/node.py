from dataclasses import dataclass, field
from typing import List, Any
from classes.symbol_table import SymbolTable

@dataclass
class Node():
    value : Any
    children : List[Any] = field(default_factory=list)

    def evaluate(self, symbol_table : SymbolTable):
        pass

    def collect_identifiers(self) -> List[str]:
        ids = []
        for c in self.children:
            # assume every Node subclass has collect_identifiers
            ids.extend(c.collect_identifiers())
        return ids
