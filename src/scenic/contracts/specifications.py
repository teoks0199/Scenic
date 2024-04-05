from abc import ABC, abstractmethod
import ast
from copy import deepcopy
from itertools import zip_longest

import scenic.core.propositions as propositions


class SpecNode(ABC):
    @staticmethod
    def propToSpec(prop, syntaxTrees):
        assert isinstance(prop, propositions.PropositionNode)

        if isinstance(prop, propositions.Atomic):
            syntaxTree = deepcopy(syntaxTrees[prop.syntax_id])
            return Atomic(syntaxTree, prop.source)
        elif isinstance(prop, propositions.Always):
            return Always(SpecNode.propToSpec(prop.req, syntaxTrees))
        elif isinstance(prop, propositions.Eventually):
            return Eventually(SpecNode.propToSpec(prop.req, syntaxTrees))
        elif isinstance(prop, propositions.Next):
            return Next(SpecNode.propToSpec(prop.req, syntaxTrees))
        elif isinstance(prop, propositions.Not):
            return Not(SpecNode.propToSpec(prop.req, syntaxTrees))
        elif isinstance(prop, propositions.Until):
            return Until(
                SpecNode.propToSpec(prop.lhs, syntaxTrees),
                SpecNode.propToSpec(prop.rhs, syntaxTrees),
            )
        elif isinstance(prop, propositions.Implies):
            return Implies(
                SpecNode.propToSpec(prop.lhs, syntaxTrees),
                SpecNode.propToSpec(prop.rhs, syntaxTrees),
            )
        elif isinstance(prop, propositions.And):
            return And([SpecNode.propToSpec(req, syntaxTrees) for req in prop.reqs])
        elif isinstance(prop, propositions.Or):
            return Or([SpecNode.propToSpec(req, syntaxTrees) for req in prop.reqs])
        else:
            assert False

    @abstractmethod
    def applyAtomicTransformer(transformer):
        pass

    @staticmethod
    def syntaxTreeToSyntaxVal(targetTree, syntaxMappings):
        # Check if there's a tree in the mappings that's equivalent to this one
        for existingTree in syntaxMappings:
            if equivalentAST(targetTree, existingTree):
                return syntaxMappings[existingTree]

        syntaxMappings[targetTree] = len(syntaxMappings)
        return syntaxMappings[targetTree]

    @staticmethod
    def equivalentAST(node1, node2):
        if type(node1) is not type(node2):
            return False

        if isinstance(node1, ast.AST):
            for name, val in vars(node1).items():
                if name in {
                    "lineno",
                    "end_lineno",
                    "col_offset",
                    "end_col_offset",
                    "ctx",
                }:
                    continue
                if not equivalentAST(val, getattr(node2, name)):
                    return False
            return True

        elif isinstance(node1, list) and isinstance(node2, list):
            return all(equivalentAST(n1, n2) for n1, n2 in zip_longest(node1, node2))
        else:
            return node1 == node2


class Atomic(SpecNode):
    def __init__(self, ast, source_str=None):
        self.ast = ast
        self.source_str = source_str

    def applyAtomicTransformer(transformer):
        self.ast = transformer.visit(self.ast)

    def __eq__(self, other):
        return type(self) is type(other) and SpecNode.equivalentAST(self.ast, other.ast)

    def __str__(self):
        return self.source_str if self.source_str else "Atomic"


class UnarySpecNode(SpecNode):
    def __init__(self, sub):
        assert isinstance(sub, SpecNode)
        self.sub = sub

    def applyAtomicTransformer(transformer):
        applyAtomicTransformer(self.sub)

    def __eq__(self, other):
        return type(self) is type(other) and self.sub == other.sub


class BinarySpecNode(SpecNode):
    def __init__(self, sub1, sub2):
        assert isinstance(sub1, SpecNode) and isinstance(sub2, SpecNode)
        self.sub1, self.sub2 = sub1, sub2

    def applyAtomicTransformer(transformer):
        applyAtomicTransformer(self.sub1)
        applyAtomicTransformer(self.sub2)

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.sub1 == other.sub1
            and self.sub2 == other.sub2
        )


class NarySpecNode(SpecNode):
    def __init__(self, subs):
        assert all(isinstance(sub, SpecNode) for sub in subs)
        self.subs = subs

    def applyAtomicTransformer(transformer):
        for sub in self.subs:
            applyAtomicTransformer(sub)

    def __eq__(self, other):
        return type(self) is type(other) and self.subs == other.subs


class Always(UnarySpecNode):
    def __str__(self):
        return f"always ({self.sub})"


class Eventually(UnarySpecNode):
    def __str__(self):
        return f"eventually ({self.sub})"


class Next(UnarySpecNode):
    def __str__(self):
        return f"next ({self.sub})"


class Not(UnarySpecNode):
    def __str__(self):
        return f"not ({self.sub})"


class Until(BinarySpecNode):
    def __str__(self):
        return f"({self.sub1}) until ({self.sub2})"


class Implies(BinarySpecNode):
    def __str__(self):
        return f"({self.sub1}) implies ({self.sub2})"


class And(NarySpecNode):
    def __str__(self):
        return " and ".join(f"({str(sub)})" for sub in self.subs)


class Or(NarySpecNode):
    def __str__(self):
        return " or ".join(f"({str(sub)})" for sub in self.subs)
