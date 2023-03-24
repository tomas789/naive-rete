from rete.common import BetaNode, Token
from rete.join_node import JoinNode
from typing import Any
from typing import Optional
from typing import Union
from rete.common import WME
from typing import Dict


class BetaMemory(BetaNode):

    kind = 'beta-memory'

    def __init__(self, children: Optional[Any] = None, parent: Union[BetaNode, JoinNode] = None, items: Optional[Any] = None) -> None:
        """
        :type items: list of Token
        """
        super(BetaMemory, self).__init__(children=children, parent=parent)
        self.items = items if items else []
        self.children = children if children else []

    def left_activation(self, token: Token, wme: WME, binding: Dict[str, str] = None) -> None:
        """
        :type binding: dict
        :type wme: WME
        :type token: Token
        """
        new_token = Token(token, wme, node=self, binding=binding)
        self.items.append(new_token)
        for child in self.children:
            child.left_activation(new_token)
