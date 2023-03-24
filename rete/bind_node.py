import copy
from rete.common import BetaNode
from rete.join_node import JoinNode
from typing import List
from rete.common import Token
from rete.common import WME
from typing import Any
from typing import Dict


class BindNode(BetaNode):

    kind = 'bind-node'

    def __init__(self, children: List, parent: JoinNode, tmpl: str, to: str) -> None:
        """
        :type children:
        :type parent: BetaNode
        :type to: str
        """
        super(BindNode, self).__init__(children=children, parent=parent)
        self.tmpl = tmpl
        self.bind = to

    def left_activation(self, token: Token, wme: WME, binding: Dict[str, Any] = None) -> None:
        """
        :type binding: dict
        :type wme: WME
        :type token: Token
        """
        code = self.tmpl
        all_binding = token.all_binding()
        all_binding.update(binding)
        for k in all_binding:
            code = code.replace(k, str(all_binding[k]))
        result = eval(code)
        binding[self.bind] = result
        for child in self.children:
            binding = copy.deepcopy(binding)
            child.left_activation(token, wme, binding)
