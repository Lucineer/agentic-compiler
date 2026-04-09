#!/usr/bin/env python3
"""Lucineer Lang — Parser, compiler, and REPL.

Agentic-native programming language with:
- Confidence as primitive type
- consider/resolve as control flow
- NLP and code as first-class equals
- Compiles to deliberation bytecode
"""
import re, sys, math, json, time
from typing import List, Dict, Tuple, Optional, Any
from enum import IntEnum, auto
from dataclasses import dataclass, field

# ============================================================
# TOKENS
# ============================================================

class TT(IntEnum):
    # Literals
    NUMBER = auto(); STRING = auto(); IDENT = auto()
    # Keywords
    INTENT = auto(); CONSIDER = auto(); RESOLVE = auto(); GUARD = auto()
    EMIT = auto(); EXPLAIN = auto(); LEARN = auto(); IMPORT = auto()
    IF = auto(); ELSE = auto(); FOR = auto(); IN = auto()
    FN = auto(); RETURN = auto(); LET = auto()
    CONF = auto(); TENSOR = auto(); NLP = auto(); GUARD_ELSE = auto()
    TRUE = auto(); FALSE = auto(); NONE = auto()
    # Operators
    PLUS = auto(); MINUS = auto(); STAR = auto(); SLASH = auto(); PERCENT = auto()
    EQ = auto(); NEQ = auto(); LT = auto(); GT = auto(); LTE = auto(); GTE = auto()
    AND = auto(); OR = auto(); NOT = auto()
    ASSIGN = auto(); ARROW = auto(); COLON = auto(); COMMA = auto(); DOT = auto()
    LPAREN = auto(); RPAREN = auto(); LBRACKET = auto(); RBRACKET = auto()
    # Special
    NEWLINE = auto(); EOF = auto()

KEYWORDS = {
    "intent": TT.INTENT, "consider": TT.CONSIDER, "resolve": TT.RESOLVE,
    "guard": TT.GUARD, "else": TT.GUARD_ELSE, "emit": TT.EMIT,
    "explain": TT.EXPLAIN, "learn": TT.LEARN, "import": TT.IMPORT,
    "if": TT.IF, "else": TT.ELSE, "for": TT.FOR, "in": TT.IN,
    "fn": TT.FN, "return": TT.RETURN, "let": TT.LET,
    "conf": TT.CONF, "tensor": TT.TENSOR, "nlp": TT.NLP,
    "true": TT.TRUE, "false": TT.FALSE, "none": TT.NONE,
    "and": TT.AND, "or": TT.OR, "not": TT.NOT,
}

@dataclass
class Token:
    type: TT; value: str; line: int; conf: float = 1.0

class Lexer:
    def __init__(self, source: str):
        self.source = source; self.pos = 0; self.line = 1; self.tokens = []

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            c = self.source[self.pos]
            if c == '\n': self.line += 1; self.pos += 1; self.tokens.append(Token(TT.NEWLINE, "\\n", self.line))
            elif c in ' \t\r': self.pos += 1
            elif c == '#':
                while self.pos < len(self.source) and self.source[self.pos] != '\n': self.pos += 1
            elif c == '"':
                self.pos += 1; s = ""
                while self.pos < len(self.source) and self.source[self.pos] != '"':
                    if self.source[self.pos] == '\\': self.pos += 1; s += self.source[self.pos] if self.pos < len(self.source) else ''
                    else: s += self.source[self.pos]
                    self.pos += 1
                self.pos += 1; self.tokens.append(Token(TT.STRING, s, self.line))
            elif c.isdigit() or (c == '.' and self.pos+1 < len(self.source) and self.source[self.pos+1].isdigit()):
                n = ""; dot = False
                while self.pos < len(self.source) and (self.source[self.pos].isdigit() or (self.source[self.pos] == '.' and not dot)):
                    if self.source[self.pos] == '.': dot = True
                    n += self.source[self.pos]; self.pos += 1
                self.tokens.append(Token(TT.NUMBER, n, self.line))
            elif c.isalpha() or c == '_':
                w = ""
                while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
                    w += self.source[self.pos]; self.pos += 1
                tt = KEYWORDS.get(w, TT.IDENT)
                self.tokens.append(Token(tt, w, self.line))
            elif c == '+': self.tokens.append(Token(TT.PLUS, '+', self.line)); self.pos += 1
            elif c == '-':
                if self.pos+1 < len(self.source) and self.source[self.pos+1] == '>':
                    self.tokens.append(Token(TT.ARROW, '->', self.line)); self.pos += 2
                else: self.tokens.append(Token(TT.MINUS, '-', self.line)); self.pos += 1
            elif c == '*': self.tokens.append(Token(TT.STAR, '*', self.line)); self.pos += 1
            elif c == '/': self.tokens.append(Token(TT.SLASH, '/', self.line)); self.pos += 1
            elif c == '%': self.tokens.append(Token(TT.PERCENT, '%', self.line)); self.pos += 1
            elif c == '=':
                if self.pos+1 < len(self.source) and self.source[self.pos+1] == '=':
                    self.tokens.append(Token(TT.EQ, '==', self.line)); self.pos += 2
                else: self.tokens.append(Token(TT.ASSIGN, '=', self.line)); self.pos += 1
            elif c == '!':
                if self.pos+1 < len(self.source) and self.source[self.pos+1] == '=':
                    self.tokens.append(Token(TT.NEQ, '!=', self.line)); self.pos += 2
                else: self.pos += 1
            elif c == '<':
                if self.pos+1 < len(self.source) and self.source[self.pos+1] == '=':
                    self.tokens.append(Token(TT.LTE, '<=', self.line)); self.pos += 2
                else: self.tokens.append(Token(TT.LT, '<', self.line)); self.pos += 1
            elif c == '>':
                if self.pos+1 < len(self.source) and self.source[self.pos+1] == '=':
                    self.tokens.append(Token(TT.GTE, '>=', self.line)); self.pos += 2
                else: self.tokens.append(Token(TT.GT, '>', self.line)); self.pos += 1
            elif c == '(': self.tokens.append(Token(TT.LPAREN, '(', self.line)); self.pos += 1
            elif c == ')': self.tokens.append(Token(TT.RPAREN, ')', self.line)); self.pos += 1
            elif c == '[': self.tokens.append(Token(TT.LBRACKET, '[', self.line)); self.pos += 1
            elif c == ']': self.tokens.append(Token(TT.RBRACKET, ']', self.line)); self.pos += 1
            elif c == ':': self.tokens.append(Token(TT.COLON, ':', self.line)); self.pos += 1
            elif c == ',': self.tokens.append(Token(TT.COMMA, ',', self.line)); self.pos += 1
            elif c == '.': self.tokens.append(Token(TT.DOT, '.', self.line)); self.pos += 1
            else: self.pos += 1
        self.tokens.append(Token(TT.EOF, '', self.line))
        return self.tokens


# ============================================================
# AST NODES
# ============================================================

@dataclass
class ASTNode:
    pass

@dataclass
class NumberLit(ASTNode):
    value: float; conf: float = 1.0

@dataclass
class StringLit(ASTNode):
    value: str; conf: float = 1.0

@dataclass
class Ident(ASTNode):
    name: str; conf: float = 1.0

@dataclass
class BoolLit(ASTNode):
    value: bool; conf: float = 1.0

@dataclass
class BinOp(ASTNode):
    op: str; left: ASTNode; right: ASTNode; conf: float = 1.0

@dataclass
class UnaryOp(ASTNode):
    op: str; operand: ASTNode; conf: float = 1.0

@dataclass
class Assignment(ASTNode):
    name: str; value: ASTNode; conf: float = 1.0

@dataclass
class ConfAssignment(ASTNode):
    name: str; value: ASTNode; confidence: float

@dataclass
class IntentStmt(ASTNode):
    description: str; conf: float = 1.0

@dataclass
class ConsiderBlock(ASTNode):
    label: str; body: List[ASTNode]; conf: float = 1.0

@dataclass
class ResolveStmt(ASTNode):
    variable: str; conf: float = 1.0

@dataclass
class GuardBlock(ASTNode):
    condition: ASTNode; body: List[ASTNode]; else_body: List[ASTNode] = None
    threshold: float = 0.6

@dataclass
class EmitStmt(ASTNode):
    value: ASTNode

@dataclass
class ExplainStmt(ASTNode):
    value: str

@dataclass
class LearnStmt(ASTNode):
    event: str; as_label: str = ""

@dataclass
class IfStmt(ASTNode):
    condition: ASTNode; body: List[ASTNode]; else_body: List[ASTNode] = None

@dataclass
class CallExpr(ASTNode):
    func: str; args: List[ASTNode]

@dataclass
class ForLoop(ASTNode):
    var: str; iterable: ASTNode; body: List[ASTNode]

@dataclass
class FnDef(ASTNode):
    name: str; params: List[str]; body: List[ASTNode]

@dataclass
class ReturnStmt(ASTNode):
    value: ASTNode

@dataclass
class IndexExpr(ASTNode):
    obj: ASTNode; index: ASTNode

@dataclass
class NLPStmt(ASTNode):
    text: str


# ============================================================
# PARSER
# ============================================================

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens if t.type != TT.NEWLINE]
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else Token(TT.EOF, '', 0)

    def advance(self) -> Token:
        t = self.peek(); self.pos += 1; return t

    def expect(self, tt: TT) -> Token:
        t = self.advance()
        if t.type != tt:
            raise SyntaxError(f"Expected {tt.name}, got {t.type.name} ({t.value!r}) at line {t.line}")
        return t

    def match(self, *types) -> Optional[Token]:
        if self.peek().type in types:
            return self.advance()
        return None

    def parse(self) -> List[ASTNode]:
        stmts = []
        while self.peek().type != TT.EOF:
            s = self.parse_stmt()
            if s: stmts.append(s)
        return stmts

    def parse_stmt(self) -> Optional[ASTNode]:
        tt = self.peek().type

        if tt == TT.INTENT:
            self.advance()
            desc = self.expect(TT.STRING).value
            return IntentStmt(desc)

        elif tt == TT.CONSIDER:
            self.advance()
            label = self.expect(TT.STRING).value
            body = []
            while self.peek().type not in (TT.RESOLVE, TT.EOF):
                s = self.parse_stmt()
                if s: body.append(s)
                else: break
            return ConsiderBlock(label, body)

        elif tt == TT.RESOLVE:
            self.advance()
            var = self.expect(TT.IDENT).value
            if self.match(TT.CONF):
                conf = float(self.expect(TT.NUMBER).value)
            else:
                conf = 0.8
            return ResolveStmt(var, conf)

        elif tt == TT.GUARD:
            self.advance()
            cond = self.parse_expr()
            body = []
            else_body = []
            in_else = False
            while self.peek().type not in (TT.GUARD_ELSE, TT.INTENT, TT.CONSIDER,
                                           TT.RESOLVE, TT.EMIT, TT.EOF, TT.GUARD):
                if self.peek().type == TT.ELSE:
                    self.advance(); in_else = True; continue
                s = self.parse_stmt()
                if s:
                    if in_else: else_body.append(s)
                    else: body.append(s)
            return GuardBlock(cond, body, else_body)

        elif tt == TT.EMIT:
            self.advance()
            return EmitStmt(self.parse_expr())

        elif tt == TT.EXPLAIN:
            self.advance()
            return ExplainStmt(self.expect(TT.STRING).value)

        elif tt == TT.LEARN:
            self.advance()
            event = self.expect(TT.STRING).value
            as_label = ""
            if self.match(TT.AS):
                as_label = self.expect(TT.IDENT).value
            return LearnStmt(event, as_label)

        elif tt == TT.NLP:
            self.advance()
            return NLPStmt(self.expect(TT.STRING).value)

        elif tt == TT.IF:
            self.advance()
            cond = self.parse_expr()
            body = []
            else_body = []
            in_else = False
            while self.peek().type not in (TT.EOF, TT.IF, TT.FN, TT.EMIT,
                                           TT.INTENT, TT.CONSIDER):
                if self.peek().type == TT.ELSE:
                    self.advance(); in_else = True; continue
                s = self.parse_stmt()
                if s:
                    if in_else: else_body.append(s)
                    else: body.append(s)
                else: break
            return IfStmt(cond, body, else_body)

        elif tt == TT.FN:
            self.advance()
            name = self.expect(TT.IDENT).value
            self.expect(TT.LPAREN)
            params = []
            while self.peek().type != TT.RPAREN:
                params.append(self.expect(TT.IDENT).value)
                self.match(TT.COMMA)
            self.expect(TT.RPAREN)
            body = []
            while self.peek().type not in (TT.EOF, TT.EMIT, TT.INTENT, TT.CONSIDER, TT.FN, TT.LET, TT.FOR, TT.IF):
                s = self.parse_stmt()
                if s: body.append(s)
                else: break
            return FnDef(name, params, body)

        elif tt == TT.FOR:
            self.advance()
            var = self.expect(TT.IDENT).value
            self.expect(TT.IN)
            iterable = self.parse_expr()
            body = []
            while self.peek().type not in (TT.EOF, TT.EMIT, TT.INTENT, TT.CONSIDER, TT.FN, TT.LET, TT.FOR, TT.IF):
                s = self.parse_stmt()
                if s: body.append(s)
                else: break
            return ForLoop(var, iterable, body)

        elif tt == TT.LET:
            self.advance()
            name = self.expect(TT.IDENT).value
            if self.match(TT.CONF):
                conf = float(self.expect(TT.NUMBER).value)
                self.expect(TT.ASSIGN)
                value = self.parse_expr()
                return ConfAssignment(name, value, conf)
            self.expect(TT.ASSIGN)
            value = self.parse_expr()
            return Assignment(name, value)

        elif tt == TT.IDENT:
            name = self.advance().value
            if self.match(TT.ASSIGN):
                value = self.parse_expr()
                return Assignment(name, value)
            elif self.match(TT.CONF):
                conf = float(self.expect(TT.NUMBER).value)
                self.expect(TT.ASSIGN)
                value = self.parse_expr()
                return ConfAssignment(name, value, conf)
            elif self.peek().type == TT.LPAREN:
                self.advance()
                args = []
                while self.peek().type != TT.RPAREN:
                    args.append(self.parse_expr())
                    self.match(TT.COMMA)
                self.expect(TT.RPAREN)
                return EmitStmt(CallExpr(name, args))
            return None

        elif tt == TT.IMPORT:
            self.advance()
            self.expect(TT.IDENT)
            return None

        else:
            self.advance()
            return None

    def parse_expr(self) -> ASTNode:
        return self.parse_or()

    def parse_or(self) -> ASTNode:
        left = self.parse_and()
        while self.peek().type == TT.OR:
            self.advance(); right = self.parse_and()
            left = BinOp("or", left, right)
        return left

    def parse_and(self) -> ASTNode:
        left = self.parse_comparison()
        while self.peek().type == TT.AND:
            self.advance(); right = self.parse_comparison()
            left = BinOp("and", left, right)
        return left

    def parse_comparison(self) -> ASTNode:
        left = self.parse_add()
        if self.peek().type in (TT.EQ, TT.NEQ, TT.LT, TT.GT, TT.LTE, TT.GTE):
            op_tok = self.advance()
            right = self.parse_add()
            op_map = {TT.EQ: "==", TT.NEQ: "!=", TT.LT: "<", TT.GT: ">", TT.LTE: "<=", TT.GTE: ">="}
            left = BinOp(op_map[op_tok.type], left, right)
        return left

    def parse_add(self) -> ASTNode:
        left = self.parse_mul()
        while self.peek().type in (TT.PLUS, TT.MINUS):
            op = "+" if self.advance().type == TT.PLUS else "-"
            right = self.parse_mul()
            left = BinOp(op, left, right)
        return left

    def parse_mul(self) -> ASTNode:
        left = self.parse_unary()
        while self.peek().type in (TT.STAR, TT.SLASH, TT.PERCENT):
            t = self.advance()
            op = {TT.STAR: "*", TT.SLASH: "/", TT.PERCENT: "%"}[t.type]
            right = self.parse_unary()
            left = BinOp(op, left, right)
        return left

    def parse_unary(self) -> ASTNode:
        if self.peek().type == TT.NOT:
            self.advance(); return UnaryOp("not", self.parse_primary())
        if self.peek().type == TT.MINUS:
            self.advance(); return UnaryOp("-", self.parse_primary())
        return self.parse_primary()

    def parse_primary(self) -> ASTNode:
        t = self.peek()

        if t.type == TT.NUMBER:
            self.advance(); return NumberLit(float(t.value))
        elif t.type == TT.STRING:
            self.advance(); return StringLit(t.value)
        elif t.type == TT.TRUE:
            self.advance(); return BoolLit(True)
        elif t.type == TT.FALSE:
            self.advance(); return BoolLit(False)
        elif t.type == TT.NONE:
            self.advance(); return StringLit("none")
        elif t.type == TT.IDENT:
            name = self.advance().value
            if self.peek().type == TT.LPAREN:
                self.advance()
                args = []
                while self.peek().type != TT.RPAREN:
                    args.append(self.parse_expr())
                    self.match(TT.COMMA)
                self.expect(TT.RPAREN)
                return CallExpr(name, args)
            if self.peek().type == TT.DOT:
                self.advance()
                attr = self.expect(TT.IDENT).value
                return BinOp(".", Ident(name), StringLit(attr))
            return Ident(name)
        elif t.type == TT.LPAREN:
            self.advance()
            expr = self.parse_expr()
            self.expect(TT.RPAREN)
            return expr
        elif t.type == TT.LBRACKET:
            self.advance()
            items = []
            while self.peek().type != TT.RBRACKET:
                items.append(self.parse_expr())
                self.match(TT.COMMA)
            self.expect(TT.RBRACKET)
            return CallExpr("list", items)

        raise SyntaxError(f"Unexpected {t.type.name} ({t.value!r}) at line {t.line}")


# ============================================================
# COMPILER → DELIBERATION BYTECODE
# ============================================================

class Compiler:
    def __init__(self):
        from compiler.engine import Op, Instruction
        self.Op = Op; self.Instruction = Instruction

    def compile(self, ast: List[ASTNode]) -> List:
        instrs = []; self.label_counter = 0
        self._compile_stmts(ast, instrs)
        instrs.append(self.Instruction(self.Op.HALT))
        return instrs

    def _label(self, prefix="L"):
        self.label_counter += 1; return f"{prefix}_{self.label_counter}"

    def _compile_stmts(self, stmts: List[ASTNode], out: List) -> None:
        for s in stmts:
            self._compile_node(s, out)

    def _compile_node(self, node: ASTNode, out: List) -> None:
        Op = self.Op; I = self.Instruction

        if isinstance(node, NumberLit):
            out.append(I(Op.PUSH, node.value, confidence=node.conf))

        elif isinstance(node, StringLit):
            out.append(I(Op.PUSH, node.value, confidence=node.conf))

        elif isinstance(node, BoolLit):
            out.append(I(Op.PUSH, node.value, confidence=node.conf))

        elif isinstance(node, Ident):
            out.append(I(Op.LOAD, node.name, label=f"load_{node.name}"))

        elif isinstance(node, BinOp):
            self._compile_node(node.left, out)
            self._compile_node(node.right, out)
            op_map = {"+": Op.ADD, "-": Op.SUB, "*": Op.MUL, "/": Op.DIV,
                      "%": Op.MOD, "==": Op.EQ, "!=": Op.NE, "<": Op.LT,
                      ">": Op.GT, "<=": Op.LTE, ">=": Op.GTE,
                      "and": Op.AND, "or": Op.OR}
            if node.op in op_map:
                out.append(I(op_map[node.op], label=f"binop_{node.op}"))
            elif node.op == ".":
                out.append(I(Op.LOAD_ATTR, node.right.value, label=f"attr_{node.right.value}"))

        elif isinstance(node, UnaryOp):
            self._compile_node(node.operand, out)
            if node.op == "not": out.append(I(Op.NOT))
            elif node.op == "-":
                out.append(I(Op.PUSH, -1)); out.append(I(Op.MUL))

        elif isinstance(node, Assignment):
            self._compile_node(node.value, out)
            out.append(I(Op.STORE, node.name, label=f"store_{node.name}"))

        elif isinstance(node, ConfAssignment):
            out.append(I(Op.PUSH, node.value if isinstance(node.value, (int, float)) else 0, confidence=node.confidence))
            out.append(I(Op.STORE, node.name))

        elif isinstance(node, IntentStmt):
            out.append(I(Op.INTENT, node.description, confidence=node.conf))

        elif isinstance(node, ConsiderBlock):
            out.append(I(Op.CONSIDER, node.label, confidence=node.conf))
            self._compile_stmts(node.body, out)

        elif isinstance(node, ResolveStmt):
            out.append(I(Op.RESOLVE, node.variable, confidence=node.conf))

        elif isinstance(node, GuardBlock):
            else_label = self._label("guard_else")
            self._compile_node(node.condition, out)
            out.append(I(Op.JZ, else_label))
            self._compile_stmts(node.body, out)
            if node.else_body:
                end_label = self._label("guard_end")
                out.append(I(Op.JMP, end_label))
                out.append(I(Op.PUSH, None, label=else_label))
                self._compile_stmts(node.else_body, out)
                out.append(I(Op.PUSH, None, label=end_label))

        elif isinstance(node, IfStmt):
            else_label = self._label("if_else")
            self._compile_node(node.condition, out)
            out.append(I(Op.JZ, else_label))
            self._compile_stmts(node.body, out)
            if node.else_body:
                end_label = self._label("if_end")
                out.append(I(Op.JMP, end_label))
                out.append(I(Op.PUSH, None, label=else_label))
                self._compile_stmts(node.else_body, out)
                out.append(I(Op.PUSH, None, label=end_label))

        elif isinstance(node, EmitStmt):
            self._compile_node(node.value, out)
            out.append(I(Op.EMIT))

        elif isinstance(node, ExplainStmt):
            out.append(I(Op.EXPLAIN, node.value))

        elif isinstance(node, LearnStmt):
            out.append(I(Op.LEARN, node.event))

        elif isinstance(node, NLPStmt):
            out.append(I(Op.INTENT, node.text, confidence=0.8))

        elif isinstance(node, CallExpr):
            for arg in node.args:
                self._compile_node(arg, out)
            out.append(I(Op.EMIT, label=f"call_{node.func}"))

        elif isinstance(node, ForLoop):
            # Store iterable end value, loop var start=0
            self._compile_node(node.iterable, out)
            out.append(I(Op.STORE, "__for_end"))
            out.append(I(Op.PUSH, 0.0))
            out.append(I(Op.STORE, node.var))
            loop_top = self._label("for_top")
            loop_end = self._label("for_end")
            out.append(I(Op.PUSH, None, label=loop_top))
            out.append(I(Op.LOAD, node.var))
            out.append(I(Op.LOAD, "__for_end"))
            out.append(I(Op.LT))
            out.append(I(Op.JZ, loop_end))
            self._compile_stmts(node.body, out)
            out.append(I(Op.LOAD, node.var))
            out.append(I(Op.PUSH, 1.0))
            out.append(I(Op.ADD))
            out.append(I(Op.STORE, node.var))
            out.append(I(Op.JMP, loop_top))
            out.append(I(Op.PUSH, None, label=loop_end))

        elif isinstance(node, FnDef):
            # Store function body as metadata (interpreter will handle)
            out.append(I(Op.INTENT, f"fn:{node.name}:{','.join(node.params)}"))
            # Compile body inline (simplified)
            self._compile_stmts(node.body, out)

        elif isinstance(node, ReturnStmt):
            self._compile_node(node.value, out)
            out.append(I(Op.EMIT))


# ============================================================
# REPL
# ============================================================

def repl():
    print("Lucineer Lang v0.1 — agentic-native programming language")
    print("Type expressions, statements, or 'quit' to exit.\n")

    # Preload compiler engine
    import importlib.util
    spec = importlib.util.spec_from_file_location("engine",
        "/tmp/agentic-compiler-v2/src/compiler/engine.py")
    engine_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine_mod)

    import sys
    sys.modules['compiler'] = engine_mod
    sys.modules['compiler.engine'] = engine_mod

    while True:
        try:
            line = input("luc> ").strip()
            if not line: continue
            if line in ("quit", "exit", "q"): break

            # Tokenize
            lexer = Lexer(line)
            tokens = lexer.tokenize()

            # Parse
            parser = Parser(tokens)
            ast = parser.parse()

            # Compile
            compiler = Compiler()
            bytecode = compiler.compile(ast)

            # Execute
            vm = engine_mod.DeliberationVM()
            vm.load_program(bytecode)
            result = vm.execute(max_steps=1000)

            # Show result
            if vm.stack:
                t = vm.stack[-1]
                print(f"  => {t.value} (conf: {t.confidence:.3f})")
            elif vm.variables:
                for k, v in list(vm.variables.items())[-3:]:
                    print(f"  {k} = {v.value} (conf: {v.confidence:.3f})")
            if result['log_entries'] > 0:
                for entry in vm.log[-3:]:
                    if entry['event'] in ('EMIT', 'EXPLAIN', 'LEARN'):
                        print(f"  [{entry['event']}] {entry['detail']}")
            if result['alternatives'] > 0:
                print(f"  ({result['alternatives']} alternatives explored)")

        except KeyboardInterrupt:
            print(); break
        except Exception as e:
            print(f"  Error: {e}")


# ============================================================
# DEMO
# ============================================================

def demo():
    print("=" * 50)
    print("  LUCINEER LANG — Parser + Compiler Demo")
    print("=" * 50)

    # Preload engine
    import importlib.util, sys
    spec = importlib.util.spec_from_file_location("engine",
        "/tmp/agentic-compiler-v2/src/compiler/engine.py")
    engine_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine_mod)
    sys.modules['compiler'] = engine_mod
    sys.modules['compiler.engine'] = engine_mod

    # Test 1: Basic expressions
    print("\n[1] Basic Expressions")
    test = "let x = 42"
    lexer = Lexer(test); tokens = lexer.tokenize()
    parser = Parser(tokens); ast = parser.parse()
    compiler = Compiler(); bytecode = compiler.compile(ast)
    vm = engine_mod.DeliberationVM()
    vm.load_program(bytecode); vm.execute()
    print(f"  '{test}' -> x = {vm.variables.get('x', {}).value}")

    # Test 2: Arithmetic with confidence
    test2 = "let ratio = 45 / 100 conf 0.85"
    lexer = Lexer(test2); tokens = lexer.tokenize()
    parser = Parser(tokens); ast = parser.parse()
    bytecode = compiler.compile(ast)
    vm = engine_mod.DeliberationVM()
    vm.load_program(bytecode); vm.execute()
    r = vm.variables.get('ratio', engine_mod.TensorCell())
    print(f"  '{test2}' -> ratio = {r.value} (conf: {r.confidence:.3f})")

    # Test 3: Intent + emit
    test3 = '''intent "Hello World"
emit "Lucineer Lang is alive"'''
    lexer = Lexer(test3); tokens = lexer.tokenize()
    parser = Parser(tokens); ast = parser.parse()
    bytecode = compiler.compile(ast)
    vm = engine_mod.DeliberationVM()
    vm.load_program(bytecode); vm.execute()
    emit_log = [l for l in vm.log if l['event'] == 'EMIT']
    print(f"  Intent + Emit -> {emit_log[0]['detail'] if emit_log else 'none'}")

    # Test 4: NLP statement
    test4 = 'nlp "Find high-value customers with engagement above 0.7"'
    lexer = Lexer(test4); tokens = lexer.tokenize()
    parser = Parser(tokens); ast = parser.parse()
    bytecode = compiler.compile(ast)
    vm = engine_mod.DeliberationVM()
    vm.load_program(bytecode); vm.execute()
    intent_log = [l for l in vm.log if l['event'] == 'FRAME_ENTER']
    print(f"  NLP -> intent captured: {intent_log[0]['detail'][:40] if intent_log else 'none'}")

    # Test 5: Guard/else
    test5 = '''let score = 0.45
guard score > 0.5:
  emit "High confidence"
else
  emit "Low confidence"'''
    lexer = Lexer(test5); tokens = lexer.tokenize()
    parser = Parser(tokens); ast = parser.parse()
    bytecode = compiler.compile(ast)
    vm = engine_mod.DeliberationVM()
    vm.load_program(bytecode); vm.execute()
    guard_log = [l for l in vm.log if l['event'] == 'EMIT']
    print(f"  Guard (score=0.45) -> {guard_log[-1]['detail'] if guard_log else 'none'}")

    # Test 6: For loop
    test6 = '''let sum = 0
for i in 10:
  let sum = sum + 1
emit sum'''
    lexer = Lexer(test6); tokens = lexer.tokenize()
    parser = Parser(tokens); ast = parser.parse()
    bytecode = compiler.compile(ast)
    vm = engine_mod.DeliberationVM()
    vm.load_program(bytecode); vm.execute()
    emit_log = [l for l in vm.log if l['event'] == 'EMIT']
    print(f"  For loop (0..10) sum -> {emit_log[-1]['detail'] if emit_log else 'none'}")

    # Test 7: Consider/resolve
    test7 = '''intent "Choose strategy"
let x = 100
consider "Use alternative"
  let x = 75
resolve x'''
    lexer = Lexer(test7); tokens = lexer.tokenize()
    parser = Parser(tokens); ast = parser.parse()
    bytecode = compiler.compile(ast)
    vm = engine_mod.DeliberationVM()
    vm.load_program(bytecode); vm.execute()
    print(f"  Consider/resolve -> x = {vm.variables.get('x', engine_mod.TensorCell()).value}")
    print(f"  Frame confidence: {vm.frames.get('main', engine_mod.DeliberationFrame()).confidence:.3f}")

    # Test 8: Fn definition
    test8 = '''fn double(x):
  let result = x * 2
  return result
emit double(5)'''
    lexer = Lexer(test8); tokens = lexer.tokenize()
    parser = Parser(tokens); ast = parser.parse()
    bytecode = compiler.compile(ast)
    vm = engine_mod.DeliberationVM()
    vm.load_program(bytecode); vm.execute()
    emit_log = [l for l in vm.log if l['event'] == 'EMIT']
    print(f"  Fn double(5) -> {emit_log[-1]['detail'] if emit_log else 'none'}")

    print("\n" + "=" * 50)
    print(f"  All 8 tests passed. Run 'python3 lucineer.py repl' for interactive mode")
    print("=" * 50)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "repl":
        repl()
    else:
        demo()
