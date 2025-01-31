from rete.common import FIELDS
from rete.alpha import ConstantTestNode
from rete.alpha import VarConsistencyTestNode
from typing import List
from rete.alpha import AlphaMemory
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Union
from typing import Any
from rete.common import WME


class VarConsistencyTestNode:

    def __init__(self, var: str, pos: List[str], amem: Optional[Any] = None, children: Optional[Any] = None) -> None:
        self.var = var
        self.pos = pos
        self.amem = amem
        self.children = children if children else []
        self.field_to_test = pos
        self.symbol = var

    def __repr__(self):
        return "<VarConsistencyTestNode %s at %s?>" % (self.var, self.pos)

    def dump(self):
        return "%s at %s?" % (self.var, self.pos)

    def test(self, wme: WME) -> bool:
        to_compare = []
        for t in self.pos:
            to_compare.append(getattr(wme, t))

        return len(set(to_compare)) <= 1

    @staticmethod
    def build_or_share(parent: ConstantTestNode, var: str, pos: List[str]) -> VarConsistencyTestNode:

        for child in parent.children:
            if type(child) is VarConsistencyTestNode:
                if child.var == var and child.pos == pos:
                    return child

        new_node = VarConsistencyTestNode(var, pos)
        parent.children.append(new_node)
        return new_node

    def activation(self, wme: WME) -> Optional[bool]:

        if not self.test(wme):
            return False

        if self.amem:
            self.amem.activation(wme)
        for child in self.children:
            child.activation(wme)


class ConstantTestNode:

    def __init__(self, field_to_test: str, field_must_equal: Optional[str] = None, amem: Optional[AlphaMemory] = None, children: Optional[List] = None, variables: Optional[Dict[str, List[str]]] = None) -> None:
        """
        :type field_to_test: str
        :type children: list of ConstantTestNode
        :type amem: AlphaMemory
        """
        self.field_to_test = field_to_test
        self.field_must_equal = field_must_equal
        self.amem = amem
        self.children = children if children else []
        self.variables = variables if variables else {}

    def __repr__(self):
        return "<ConstantTestNode %s=%s?>" % (self.field_to_test, self.field_must_equal)

    def dump(self):
        return "%s=%s?" % (self.field_to_test, self.field_must_equal)

    def _constant_check(self, wme: WME) -> bool:
        v = getattr(wme, self.field_to_test)
        if v != self.field_must_equal:
            return False
        else:
            return True

    def _variables_check(self, wme: WME) -> bool:

        to_compare = []

        for var, slots in self.variables.items():
            if len(slots) > 1:
                to_compare = []
                for t in slots:
                    to_compare.append(getattr(wme, t))

        return len(set(to_compare)) <= 1

    def activation(self, wme: WME) -> Optional[bool]:
        """
        :type wme: rete.WME
        """
        if self.field_to_test != 'no-test':

            if not self._variables_check(wme):
                return False

            if not self._constant_check(wme):
                return False

        if self.amem:
            self.amem.activation(wme)
        for child in self.children:
            child.activation(wme)

    @classmethod
    def build_or_share_alpha_memory(cls, node: Union[ConstantTestNode, VarConsistencyTestNode], constants: List[Tuple[str, str]] = None, variables: Optional[Dict[str, List[str]]] = None) -> AlphaMemory:
        """
        :type node: ConstantTestNode
        :type path: [(field, value)...]
        :rtype: AlphaMemory
        """
        constants = constants if constants else []

        # no constants to check
        if not len(constants):
            # return the existing alpha memory or create a new one
            if not node.amem:
                node.amem = AlphaMemory()

            return node.amem

        f, v = constants.pop(0)
        assert f in FIELDS, "`%s` not in %s" % (f, FIELDS)
        next_node = cls.build_or_share_constant_test_node(node, f, v, variables)

        # recursion
        return cls.build_or_share_alpha_memory(next_node, constants)

    @staticmethod
    def build_or_share_constant_test_node(parent: ConstantTestNode, field: str, symbol: str, variables: Optional[Dict[str, List[str]]]) -> ConstantTestNode:
        """
        :rtype: ConstantTestNode
        :type symbol: str
        :type field: str
        :type parent: ConstantTestNode
        """
        for child in parent.children:
            if child.field_to_test == field and child.field_must_equal == symbol:
                return child
        new_node = ConstantTestNode(field, symbol, children=[], variables=variables)
        parent.children.append(new_node)
        return new_node


class AlphaMemory:

    def __init__(self, items: Optional[Any] = None, successors: Optional[Any] = None) -> None:
        """
        :type successors: list of BetaNode
        :type items: list of rete.WME
        """
        self.items = items if items else []
        self.successors = successors if successors else []

    def activation(self, wme: WME) -> None:
        """
        :type wme: rete.WME
        """
        if wme in self.items:
            return
        self.items.append(wme)
        wme.amems.append(self)
        for child in reversed(self.successors):
            child.right_activation(wme)
