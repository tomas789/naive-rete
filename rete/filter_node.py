import copy
from rete.common import BetaNode
from rete.bind_node import BindNode
from rete.filter_node import FilterNode
from rete.join_node import JoinNode
from typing import List
from typing import Union
from rete.common import Token
from rete.common import WME
from typing import Any
from typing import Dict


class FilterNode(BetaNode):

    kind = 'filter-node'

    def __init__(self, children: List, parent: Union[BindNode, FilterNode, JoinNode], tmpl: str) -> None:
        """
        :type children:
        :type parent: BetaNode
        :type bind: str
        """
        super(FilterNode, self).__init__(children=children, parent=parent)
        self.tmpl = tmpl

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
        if bool(result):
            for child in self.children:
                child.left_activation(token, wme, binding)
