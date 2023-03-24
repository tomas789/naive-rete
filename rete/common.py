from typing import List
from typing import Tuple
from rete.common import WME
from typing import Optional
from typing import Union
from rete.common import Token
from typing import Any
from rete.common import Has
from rete.common import Filter
from rete.common import Bind
from typing import Dict
# -*- coding: utf-8 -*-

FIELDS = ['identifier', 'attribute', 'value']


class BetaNode(object):

    def __init__(self, children: Optional[List] = None, parent: Any = None) -> None:
        self.children = children if children else []
        self.parent = parent

    def dump(self):
        return "%s %s" % (self.__class__.__name__, id(self))


class Has:

    def __init__(self, identifier: str = None, attribute: str = None, value: str = None) -> None:
        """
        (<x> ^self <y>)
        repr as:
        ('$x', 'self', '$y')

        :type value: Var or str
        :type attribute: Var or str
        :type identifier: Var or str
        """
        self.identifier = identifier
        self.attribute = attribute
        self.value = value

    def __repr__(self):
        return "(%s %s %s)" % (self.identifier, self.attribute, self.value)

    def __eq__(self, other: Has) -> bool:
        return self.__class__ == other.__class__ \
               and self.identifier == other.identifier \
               and self.attribute == other.attribute \
               and self.value == other.value

    @property
    def vars(self) -> List[Tuple[str, str]]:
        """
        :rtype: list
        """
        ret = []
        for field in FIELDS:
            v = getattr(self, field)
            if is_var(v):
                ret.append((field, v))
        return ret

    def contain(self, v: str) -> str:
        """
        :type v: Var
        :rtype: bool
        """
        for f in FIELDS:
            _v = getattr(self, f)
            if _v == v:
                return f
        return ""

    def test(self, w: WME) -> bool:
        """
        :type w: rete.WME
        """
        for f in FIELDS:
            v = getattr(self, f)
            if is_var(v):
                continue
            if v != getattr(w, f):
                return False
        return True


class Neg(Has):

    def __repr__(self):
        return "-(%s %s %s)" % (self.identifier, self.attribute, self.value)


class Rule(list):

    def __init__(self, *args: Any) -> None:
        self.extend(args)


class Ncc(Rule):

    def __repr__(self):
        return "-%s" % super(Ncc, self).__repr__()

    @property
    def number_of_conditions(self) -> int:
        return len(self)


class Filter:
    def __init__(self, tmpl: str) -> None:
        self.tmpl = tmpl

    def __eq__(self, other: Filter) -> bool:
        return isinstance(other, Filter) and self.tmpl == other.tmpl


class Bind:
    def __init__(self, tmp: str, to: str) -> None:
        self.tmpl = tmp
        self.to = to

    def __eq__(self, other: Bind) -> bool:
        return isinstance(other, Bind) and \
               self.tmpl == other.tmpl and self.to == other.to


class WME:

    def __init__(self, identifier: str, attribute: str, value: str) -> None:
        self.identifier = identifier
        self.attribute = attribute
        self.value = value
        self.amems = []  # the ones containing this WME
        self.tokens = []  # the ones containing this WME
        self.negative_join_result = []

    def __repr__(self):
        return "(%s ^%s %s)" % (self.identifier, self.attribute, self.value)

    def __eq__(self, other: WME) -> bool:
        """
        :type other: WME
        """
        if not isinstance(other, WME):
            return False
        return self.identifier == other.identifier and \
            self.attribute == other.attribute and \
            self.value == other.value


class Token:

    def __init__(self, parent: Optional[Token], wme: Optional[WME], node: Any = None, binding: Optional[Dict[str, str]] = None) -> None:
        """
        :type wme: WME
        :type parent: Token
        :type binding: dict
        """
        self.parent = parent
        self.wme = wme
        self.node = node  # points to memory this token is in
        self.children = []  # the ones with parent = this token
        self.join_results = []  # used only on tokens in negative nodes
        self.ncc_results = []
        self.owner = None  # Ncc
        self.binding = binding if binding else {}  # {"$x": "B1"}

        if self.wme:
            self.wme.tokens.append(self)
        if self.parent:
            self.parent.children.append(self)

    def __repr__(self):
        return "<Token %s>" % self.wmes

    def __eq__(self, other: Optional[Token]) -> bool:
        return isinstance(other, Token) and \
               self.parent == other.parent and self.wme == other.wme

    def is_root(self) -> bool:
        return not self.parent and not self.wme

    @property
    def wmes(self) -> Union[List[Optional[WME]], List[WME]]:
        ret = [self.wme]
        t = self
        while not t.parent.is_root():
            t = t.parent
            ret.insert(0, t.wme)
        return ret

    def get_binding(self, v: str) -> Union[int, str]:
        t = self
        ret = t.binding.get(v)
        while not ret and t.parent:
            t = t.parent
            ret = t.binding.get(v)
        return ret

    def all_binding(self) -> Dict:
        path = [self]
        if path[0].parent:
            path.insert(0, path[0].parent)
        binding = {}
        for t in path:
            binding.update(t.binding)
        return binding

    @classmethod
    def delete_token_and_descendents(cls, token: Token) -> None:
        """
        :type token: Token
        """
        from rete.negative_node import NegativeNode
        from rete.ncc_node import NccPartnerNode, NccNode

        for child in token.children:
            cls.delete_token_and_descendents(child)
        if not isinstance(token.node, NccPartnerNode):
            token.node.items.remove(token)
        if token.wme:
            token.wme.tokens.remove(token)
        if token.parent:
            token.parent.children.remove(token)
        if isinstance(token.node, NegativeNode):
            for jr in token.join_results:
                jr.wme.negative_join_result.remove(jr)
        elif isinstance(token.node, NccNode):
            for result_tok in token.ncc_results:
                result_tok.wme.tokens.remove(result_tok)
                result_tok.parent.children.remove(result_tok)
        elif isinstance(token.node, NccPartnerNode):
            token.owner.ncc_results.remove(token)
            if not token.owner.ncc_results:
                for child in token.node.ncc_node.children:
                    child.left_activation(token.owner, None)


def is_var(v: str) -> bool:
    return v.startswith('$')
