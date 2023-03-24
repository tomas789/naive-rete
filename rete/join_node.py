from rete.common import BetaNode, Has
from rete.alpha import AlphaMemory
from rete.beta_memory_node import BetaMemory
from rete.join_node import TestAtJoinNode
from typing import List
from rete.common import WME
from rete.common import Token
from typing import Dict


class JoinNode(BetaNode):

    kind = 'join-node'

    def __init__(self, children: List, parent: BetaMemory, amem: AlphaMemory, tests: List[TestAtJoinNode], has: Has) -> None:
        """
        :type children:
        :type parent: BetaNode
        :type amem: AlphaMemory
        :type tests: list of TestAtJoinNode
        :type has: Has
        """
        super(JoinNode, self).__init__(children=children, parent=parent)
        self.amem = amem
        self.tests = tests
        self.has = has

    def right_activation(self, wme: WME) -> None:
        """
        :type wme: rete.WME
        """
        for token in self.parent.items:
            if self.perform_join_test(token, wme):
                binding = self.make_binding(wme)
                for child in self.children:
                    child.left_activation(token, wme, binding)

    def left_activation(self, token: Token) -> None:
        """
        :type token: rete.Token
        """
        for wme in self.amem.items:
            if self.perform_join_test(token, wme):
                binding = self.make_binding(wme)
                for child in self.children:
                    child.left_activation(token, wme, binding)

    def perform_join_test(self, token: Token, wme: WME) -> bool:
        """
        :type token: rete.Token
        :type wme: rete.WME
        """
        for this_test in self.tests:
            arg1 = getattr(wme, this_test.field_of_arg1)
            wme2 = token.wmes[this_test.condition_number_of_arg2]
            arg2 = getattr(wme2, this_test.field_of_arg2)
            if arg1 != arg2:
                return False
        return True

    def make_binding(self, wme: WME) -> Dict[str, str]:
        """
        :type wme: WME
        """
        binding = {}
        for field, v in self.has.vars:
            val = getattr(wme, field)
            binding[v] = val
        return binding


class TestAtJoinNode:

    def __init__(self, field_of_arg1: str, condition_number_of_arg2: int, field_of_arg2: str) -> None:
        self.field_of_arg1 = field_of_arg1
        self.condition_number_of_arg2 = condition_number_of_arg2
        self.field_of_arg2 = field_of_arg2

    def __repr__(self):
        return "<TestAtJoinNode WME.%s=Condition%s.%s?>" % (
            self.field_of_arg1, self.condition_number_of_arg2, self.field_of_arg2)

    def __eq__(self, other: TestAtJoinNode) -> bool:
        return isinstance(other, TestAtJoinNode) and \
            self.field_of_arg1 == other.field_of_arg1 and \
            self.field_of_arg2 == other.field_of_arg2 and \
            self.condition_number_of_arg2 == other.condition_number_of_arg2
