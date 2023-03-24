from rete.common import BetaNode, Token
from typing import Any
from typing import Optional
from rete.common import WME
from typing import Dict


class PNode(BetaNode):

    kind = 'p'

    def __init__(self, children: Optional[Any] = None, parent: Any = None, items: Optional[Any] = None, **kwargs: Any) -> None:
        """
        :type items: list of Token
        """
        super(PNode, self).__init__(children=children, parent=parent)
        self.items = items if items else []
        self.children = children if children else []
        for k, v in kwargs.items():
            setattr(self, k, v)

    def left_activation(self, token: Token, wme: Optional[WME], binding: Optional[Dict[str, Any]] = None) -> None:
        """
        :type wme: WME
        :type token: Token
        :type binding: dict
        """
        new_token = Token(token, wme, node=self, binding=binding)
        self.items.append(new_token)

    def execute(self, *args, **kwargs):
        raise NotImplementedError
