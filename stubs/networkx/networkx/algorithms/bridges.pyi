from _typeshed import Incomplete
from collections.abc import Callable, Generator
from typing import overload
from typing_extensions import Literal

from networkx.classes.graph import Graph, _Node

def bridges(G: Graph[_Node], root: _Node | None = None) -> Generator[_Node, None, None]: ...
def has_bridges(G: Graph[_Node], root: Incomplete | None = None) -> bool: ...
@overload
def local_bridges(
    G: Graph[_Node], with_span: Literal[False], weight: str | Callable[[_Node], float] | None = None
) -> Generator[tuple[_Node, _Node], None, None]: ...
@overload
def local_bridges(
    G: Graph[_Node], with_span: Literal[True] = True, weight: str | Callable[[_Node], float] | None = None
) -> Generator[tuple[_Node, _Node, int], None, None]: ...
