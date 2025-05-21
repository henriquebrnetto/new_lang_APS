from dataclasses import dataclass, field
from typing import List, Any, Set

@dataclass
class Node():
    value : Any
    children : List[Any] = field(default_factory=list)

    def evaluate(self, symbol_table):
        """To be implemented by subclasses."""
        pass

    def collect_identifiers(self) -> Set[str]:
        """
        Recursively collects all unique identifier names (strings) from this node's children.
        Subclasses like IdentifierNode will override this to add their own value.
        Nodes that don't contain identifiers or whose children don't (e.g., literals)
        will effectively return an empty set through this base implementation if not overridden.
        """
        ids: Set[str] = set()
        for child in self.children:
            if isinstance(child, Node): 
                ids.update(child.collect_identifiers())
            
        return ids