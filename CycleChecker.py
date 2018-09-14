from lark import Lark, Transformer

dot_grammar = r"""
graph	: (graph | "digraph") [ id ] "{" stmt_list "}"
stmt_list	:	[ stmt [ ";" ] stmt_list ] -> block
stmt	:	node_stmt
|	edge_stmt
|	attr_stmt
|	id "=" id
|	subgraph
attr_stmt	:	("graph") edgerhs [attr_list]
?attr_list	:	"[" [ a_list ] "]" [ attr_list ] -> parameters
a_list	:	id "=" id [ (";" | ",") ] [ a_list ] -> equation
edge_stmt	:	(node_id | subgraph) edgerhs [ attr_list ] -> edge
edgerhs	:	edgeop (node_id | subgraph) [ edgerhs ] -> edge_assignment
node_stmt	:	node_id [ attr_list ] -> edgeless_node
node_id	:	id [ port ]
port	:	":" id [ ":" compass_pt ]
|	":" compass_pt
subgraph	:	[ id ] "{" stmt_list "}"
compass_pt	:	("n" | "ne" | "e" | "se" | "s" | "sw" | "w" | "nw" | "c")
id : UNQUOTED_STRING | SIGNED_INT | DOUBLE_QUOTED_STRING
COMMENT: /\#[^\n]*/
CCOMMENT: /\/(?s)[*].*?[*]\//
edgeop: ("->" | "--") -> connection
UNQUOTED_STRING: /[a-z0-9_:]+/i
DOUBLE_QUOTED_STRING: "\"" ("\\\""|/[^"]/)* "\"" "i"?
SIGNED_INT: ["-"|"+"] INT
INT: /[0-9]+(?![_a-zA-Z])/
_NL: /[\r\n]+/
    %import common.ESCAPED_STRING
    %import common.WS
    %ignore WS
    %ignore COMMENT
    %ignore CCOMMENT
    %ignore _NL
"""


class GraphAnalyzer:
    x = 0
    y = 0
    c = 0


class DotTree(Transformer):

    def string(self, s):
        s[1:-1].replace('\\"', '"')

    def stmt(self, j):
        GraphAnalyzer.x += 1
        return j

    def edge(self, b):
        GraphAnalyzer.y += 1
        return b

    def graph(self, n):
        GraphAnalyzer.c += 1
        return n


dot_parser = Lark(dot_grammar, start="graph", parser='lalr', transformer=DotTree())
pretty_tree = Lark(dot_grammar, start="graph", parser='lalr')
parsee = pretty_tree.parse
parse = dot_parser.parse

if __name__ == '__main__':
    with open("script.txt", "r") as f:
        print(parsee(f.read()).pretty())
        f.seek(0)
        parse(f.read())
        print("The Dot script parsed in the tree above has a cyclomatic complexity value of " +
              str(GraphAnalyzer.x - GraphAnalyzer.y + (2 * GraphAnalyzer.c)))
