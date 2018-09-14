import sys


class TokenTypes(object):
    """A singleton to represent all token types"""
    (EOF, GRAPH, ID, LABEL, CONNECTION, LBRACE, LBRACK, RBRACK, RBRACE, PARAMETER,
     COMMAND, SEMICOLON, COMMENT, VARIABLE, ASSIGNMENT, QUOTATION, STRING, EQUATION) = range(18)
    names = ['EOF', 'DIGRAPH', 'ID', 'LABEL', 'CONNECTION', 'LBRACE', 'LBRACK', 'RBRACK', 'RBRACE', 'PARAMETER',
             'COMMAND', 'SEMICOLON', 'COMMENT', 'VARIABLE', 'ASSIGNMENT', 'QUOTATION', "STRING", "EQUATION"]


class Token(object):
    """An abstract token."""

    def __init__(self, type, text, linecount):
        """Constructor
            type is a numeric token type from TokenTypes
            text is the lexeme
        """

        self.type = type
        self.text = text
        self.linecount = linecount

    def __str__(self):
        return "<'%s', %s, %s>" % (self.text, TokenTypes.names[self.type], self.linecount)


class Lexer(object):
    """My custom lexer."""

    def __init__(self, str):
        self.input = str
        self.connectionactive = 0
        self.equivalentcheck = 0
        self.quotecheck = 0
        self.p = 0
        self.c = self.input[self.p]

    def __consume(self):
        """Advance to the next character of input or EOF"""
        self.p += 1
        if self.p >= len(self.input):
            self.c = TokenTypes.EOF
        else:

            self.c = self.input[self.p]

    def next_token(self):
        """Return the next Token in the input stream, ignoring whitespace."""
        tokens = []
        linecount = 1

        while self.c != TokenTypes.EOF:
            if self.c in [' ', '\t', '\n', '\r']:
                if self.c in '\n':
                    linecount += 1

                self.__consume()

            elif self.c == '[':
                parametervalue = ""
                parametercheck1 = ""
                parametercheck2 = ""
                quotevalue = ""
                tempstore = ""
                self.__consume()
                tokens.append(Token(TokenTypes.LBRACK, '[', linecount))
                while self.c != TokenTypes.EOF and self.c != ']':
                    parametervalue += self.c
                    if self.c == '=':
                        self.equivalentcheck = 1
                        equal1 = Token(TokenTypes.VARIABLE, parametercheck1, linecount)
                        tokens.append(equal1)
                        tempstore = parametercheck1
                        parametercheck1 = ""
                    elif self.c != '=' and self.equivalentcheck == 0 and self.c != ',':
                        parametercheck1 += self.c
                    elif self.c != '=' and self.equivalentcheck == 1 and self.c != ',':
                        parametercheck2 += self.c
                    elif self.c == ',' and self.equivalentcheck == 1:
                        equal2 = Token(TokenTypes.ASSIGNMENT, parametercheck2, linecount)
                        tokens.append(equal2)
                        equal3 = Token(TokenTypes.EQUATION, tempstore + "=" + parametercheck2, linecount)
                        tokens.append(equal3)
                        tempstore = ""
                        self.equivalentcheck = 0
                        parametercheck2 = ""

                    if self.c == '"':
                        execution = 0
                        if execution != 1:
                            self.quotecheck += 1
                        if self.c == '"' and self.quotecheck == 2:
                            execution = 1
                            quotetoken = Token(TokenTypes.STRING, quotevalue, linecount)
                            tokens.append(quotetoken)
                            self.quotecheck = 0
                            quotevalue = ""

                        tokens.append(Token(TokenTypes.QUOTATION, '"', linecount))

                    if self.c != '"' and self.quotecheck > 0:
                        quotevalue += self.c

                    self.__consume()
                if parametercheck2 != "" and self.c == ']':
                    equal2 = Token(TokenTypes.ASSIGNMENT, parametercheck2, linecount)
                    tokens.append(equal2)
                    equal3 = Token(TokenTypes.EQUATION, tempstore + "=" + parametercheck2, linecount)
                    tokens.append(equal3)
                    tempstore = ""
                    self.equivalentcheck = 0
                    parametercheck2 = ""
                pval = Token(TokenTypes.PARAMETER, parametervalue, linecount)
                tokens.append(pval)
                paramtervalue = ""
                self.equivalentcheck = 0

            elif self.c == '/':
                commentvalue = ""
                commentvalue += self.c
                self.__consume()
                while self.c != TokenTypes.EOF and self.c != '/':
                    commentvalue += self.c
                    self.__consume()
                commentvalue += self.c
                cval = Token(TokenTypes.COMMENT, commentvalue, linecount)
                tokens.append(cval)
                self.__consume()

            elif self.c == '-':
                connectionvalue = ""
                connectionvalue += self.c
                self.__consume()
                while self.c != TokenTypes.EOF and self.c != '>':
                    self.__consume()
                connectionvalue += self.c
                conval = Token(TokenTypes.CONNECTION, connectionvalue, linecount)
                tokens.append(conval)
                self.__consume()
                self.connectionactive = 1

            elif self.c == '{':
                self.__consume()
                tokens.append(Token(TokenTypes.LBRACE, '{', linecount))

            elif self.c == '}':
                self.__consume()
                tokens.append(Token(TokenTypes.RBRACE, '}', linecount))


            elif self.c == ';':
                self.__consume()
                tokens.append(Token(TokenTypes.SEMICOLON, ';', linecount))
                self.connectionactive = 0

            elif self.c == ']':
                self.__consume()
                tokens.append(Token(TokenTypes.RBRACK, ']', linecount))


            elif self.c.isalpha():
                lexeme = ""
                while self.c != TokenTypes.EOF and self.c.isalpha() or self.c == '_' and lexeme != "digraph":
                    lexeme += self.c
                    self.__consume()
                if lexeme == "digraph":
                    t = Token(TokenTypes.GRAPH, lexeme, linecount)
                    tokens.append(t)
                elif self.connectionactive == 1:
                    t = Token(TokenTypes.ID, lexeme, linecount)
                    tokens.append(t)
                elif self.connectionactive == 0 and self.input[self.p - 1] == ';':
                    t = Token(TokenTypes.ID, lexeme, linecount)
                    tokens.append(t)
                else:
                    t = Token(TokenTypes.LABEL, lexeme, linecount)
                    tokens.append(t)

            else:
                sys.stderr.write("Invalid character %c." % self.c)
                self.__consume()
                # sys.exit(1)
        tokens.append(Token(TokenTypes.EOF, "<EOF>", linecount))
        return tokens


# -----------------------------------------------------------------------------
#     _    ____ _____
#    / \  / ___|_   _|
#   / _ \ \___ \ | |
#  / ___ \ ___) || |
# /_/   \_\____/ |_|

class AST(object):
    """Homogeneous AST """

    def __init__(self, token):
        """token should be of type Lexer.Token"""
        self.token = token  # node "value"
        self.children = []  # child AST nodes

    def add_child(self, t):
        self.children.append(t)

    def __str__(self):
        return str(self.token)

    def to_string_tree(self):
        """Build a string representing the entire tree."""
        if len(self.children) == 0:
            return str(self)
        buf = "(%s " % str(self.token)
        for i in range(len(self.children)):
            t = self.children[i]
            if i > 0:
                buf += " "
            buf += t.to_string_tree()
        buf += ")"
        return buf

        ###########################

        # PARSER                    #

        ###########################


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_index = 0
        self.node = AST(object)
        self.lookahead = tokens[self.tok_index + 1]
        self.brace_value = 0
        self.lbrack = 0
        self.connection_value = 0
        self.variable_value = 0
        self.quotecount = 1

    def match(self, tok_type):
        tok = self.tokens[self.tok_index]

        if tok.type == tok_type:
            return tok

    def next_token(self):
        func_tok = self.match(TokenTypes.RBRACE)
        if func_tok is None:
            self.tok_index += 1
            if self.lookahead.type != TokenTypes.EOF:
                self.lookahead = self.tokens[self.tok_index + 1]
            return self.tokens[self.tok_index]

    # def node_list(self):
    #   node = self.node_list_elements()
    #  return node

    # def node_list_elements(self):

    def parsebrace(self):
        if self.brace_value == 0:
            func_tok = self.match(TokenTypes.LBRACE)
            if func_tok is not None and func_tok.text == '{':
                self.bracevalue = 1
                self.next_token()
                self.parselist()

        if self.brace_value == 1:
            func_tok = self.match(TokenTypes.RBRACE)
            if func_tok is None and self.tokens[self.tok_index].type == TokenTypes.EOF:
                print("Expecting %s found %s at %s" % (TokenTypes.names[TokenTypes.RBRACE],
                                                       self.tokens[self.tok_index].text,
                                                       self.tokens[self.tok_index].linecount))
                exit(0)
            elif func_tok is not None:
                self.brace_value = 0
                self.next_token()

    def parselist(self):
        func_tok = self.match(TokenTypes.LBRACE)

        if func_tok is not None:
            return self.parsebrace()
        func_tok2 = self.match(TokenTypes.GRAPH)
        if func_tok2 is not None:
            return self.parse_digraph()
        func_tok4 = self.match(TokenTypes.LABEL)
        if func_tok4 is not None:
            self.next_token()
        func_tok3 = self.match(TokenTypes.CONNECTION)
        if func_tok3 is not None:
            return self.parse_ID()
        func_tok5 = self.match(TokenTypes.RBRACE)
        if func_tok5 is not None:
            return

        if self.lbrack == 0:
            func_tok = self.match(TokenTypes.LBRACK)

            if func_tok is not None and func_tok.text == '[':
                self.lbrack = 1
                self.next_token()
                node1 = self.parse_elements()
                return node1
        elif self.lbrack == 1:

            func_tok = self.match(TokenTypes.RBRACK)

            if func_tok is not None:
                self.lbrack = 0
            elif func_tok is None and ';' in self.tokens[self.tok_index].text:
                print("Expecting %s found %s at line %s" % (TokenTypes.names[TokenTypes.RBRACK],
                                                            self.tokens[self.tok_index].text,
                                                            self.tokens[self.tok_index].linecount))
                exit(0)

    def parse_ID(self):

        if self.connection_value == 0:
            func_tok = self.match(TokenTypes.CONNECTION)
            if func_tok is not None and func_tok.text == '->':
                self.connection_value = 1
                self.next_token()
        if self.connection_value == 1:
            func_tok = self.match(TokenTypes.ID)
            if func_tok is None and '[' in self.tokens[self.tok_index].text:
                print("Expecting %s found %s at line %s" % (TokenTypes.names[TokenTypes.ID],
                                                            self.tokens[self.tok_index].text,
                                                            self.tokens[self.tok_index].linecount))
                exit(0)
            elif func_tok is not None:
                if self.lookahead.type == TokenTypes.LBRACK:
                    self.next_token()
                    node = AST(func_tok)
                    node.add_child(self.parselist())
                    self.connection_value = 0
                    return node
                else:
                    self.next_token()
                    node = AST(func_tok)
                    self.connection_value = 0
                    return node

    def parse_variable(self):

        if self.variable_value == 0:
            func_tok = self.match(TokenTypes.VARIABLE)

            if func_tok is not None:
                self.variable_value = 1
                node1 = AST(func_tok)
                self.next_token()

                return node1

            elif func_tok is None and ']' in self.tokens[self.tok_index].text or ';' in \
                    self.tokens[self.tok_index].text:
                print("Expecting %s found %s at line %s" % (TokenTypes.names[TokenTypes.ASSIGNMENT],
                                                            self.tokens[self.tok_index].text,
                                                            self.tokens[self.tok_index].linecount))
        elif self.variable_value == 1:
            node1 = AST("Assignment Types")
            func_tok2 = self.match(TokenTypes.QUOTATION)
            if func_tok2 is not None:
                node1.add_child(self.parse_quote())
                self.next_token()
            func_tok = self.match(TokenTypes.ASSIGNMENT)
            if func_tok is not None:
                node2 = AST(self.parse_assignment())
                node2.children = node1.children
                self.next_token()
                return node2
            elif func_tok is None and ']' in self.tokens[self.tok_index].text or ';' or '/*' in \
                    self.tokens[self.tok_index].text:
                print("Expecting %s found %s at line %s" % (TokenTypes.names[TokenTypes.ASSIGNMENT],
                                                            self.tokens[self.tok_index + 1].text,
                                                            self.tokens[self.tok_index].linecount))
                exit(0)

    def parse_assignment(self):
        func_tok = self.match(TokenTypes.ASSIGNMENT)

        if func_tok is None and ']' in self.tokens[self.tok_index].text or ';' in \
                self.tokens[self.tok_index].text:
            print("Expecting %s found %s at line %s" % (TokenTypes.names[TokenTypes.ASSIGNMENT],
                                                        self.tokens[self.tok_index].text,
                                                        self.tokens[self.tok_index].linecount))
            exit(0)

        elif func_tok is not None:
            self.variable_value = 0
            node1 = AST(func_tok)
            return node1

    def parse_digraph(self):
        func_tok = self.match(TokenTypes.GRAPH)
        func_tok2 = self.match(TokenTypes.RBRACE)

        if func_tok is not None:
            self.node = AST(func_tok)
            if self.lookahead.type != TokenTypes.LBRACE:
                self.next_token()
                self.next_token()
                self.next_token()
            while func_tok2 is None:
                self.node.add_child(self.parse_label())
                func_tok3 = self.match(TokenTypes.LABEL)
               # print(self.node.to_string_tree())
                if func_tok3 is None:
                    self.next_token()
                func_tok2 = self.match(TokenTypes.RBRACE)
                if func_tok2 is not None:
                    return self.node
        else:
            print("Expecting %s found %s at line %s" % (TokenTypes.names[TokenTypes.GRAPH],
                                                        self.tokens[self.tok_index].text,
                                                        self.tokens[self.tok_index].linecount))
            exit(0)

    def parse_label(self):
        func_tok = self.match(TokenTypes.LABEL)
        func_tok2 = self.match(TokenTypes.SEMICOLON)
        func_tok3 = self.match(TokenTypes.COMMENT)

        if func_tok is not None:
            node1 = AST(func_tok)
            while func_tok2 is None:
                func_tok4 = self.match(TokenTypes.RBRACE)
                func_tok2 = self.match(TokenTypes.SEMICOLON)
                if func_tok2 is not None:
                    self.next_token()
                    return node1
                elif func_tok4 is not None:
                    return node1
                else:
                    func_tok2 = self.match(TokenTypes.SEMICOLON)
                    if func_tok2 is None:
                        node1.add_child(self.parselist())
                        func_tok2 = self.match(TokenTypes.SEMICOLON)
                        if func_tok2 is not None:
                            self.next_token()
                            return node1
                        else:
                            self.next_token()
                    else:
                        self.next_token()
                        return node1

        elif func_tok3 is not None:
            self.next_token()
            return self.parse_label()
        elif func_tok is None:
            print("Expecting %s found %s at line %s" % (TokenTypes.names[TokenTypes.LABEL],
                                                        self.tokens[self.tok_index].text,
                                                        self.tokens[self.tok_index].linecount))
            exit(0)

    def parse_quote(self):
        func_tok = self.match(TokenTypes.QUOTATION)
        while func_tok is not None:
            if self.lookahead.type == TokenTypes.STRING:
                node1 = AST(self.lookahead)
                self.next_token()
                if self.lookahead.type == TokenTypes.QUOTATION:
                    self.next_token()
                else:
                    print("Expecting %s found %s at line %s" % (TokenTypes.names[TokenTypes.QUOTATION],
                                                                self.tokens[self.tok_index].text,
                                                                self.tokens[self.tok_index].linecount))
                return node1

    def parse_element(self):
        func_tok2 = self.match(TokenTypes.LBRACK)
        func_tok = self.match(TokenTypes.VARIABLE)
        func_tok3 = self.match(TokenTypes.EQUATION)
        func_tok4 = self.match(TokenTypes.PARAMETER)
        node1 = AST("Equation Value")
        if func_tok2 is not None:
            return self.parselist()
        if func_tok is not None:
            t = self.parse_variable()
            node1.add_child(t)
            while func_tok4 is None:
                while func_tok3 is None:
                    t = self.parse_variable()
                    node1.add_child(t)
                    func_tok3 = self.match(TokenTypes.EQUATION)
                self.next_token()
                func_tok4 = self.match(TokenTypes.PARAMETER)
                if func_tok3 is not None:
                    node2 = AST(func_tok3)
                    node2.children = node1.children
                    return node2

    def parse_elements(self):
        func_tok = self.match(TokenTypes.EQUATION)
        func_tok2 = self.match(TokenTypes.VARIABLE)
        func_tok3 = self.match(TokenTypes.ASSIGNMENT)
        func_tok5 = self.match(TokenTypes.PARAMETER)
        if func_tok is not None or func_tok2 is not None or func_tok3 is not None:
            node1 = AST("list")
            node1.add_child(self.parse_element())
            func_tok2 = self.match(TokenTypes.VARIABLE)
            if func_tok2 is None:
                self.next_token()
            if func_tok5 is not None:
                return node1
            func_tok = self.match(TokenTypes.EQUATION)
            func_tok2 = self.match(TokenTypes.VARIABLE)
            func_tok3 = self.match(TokenTypes.ASSIGNMENT)
            func_tok4 = self.match(TokenTypes.QUOTATION)
            func_tok5 = self.match(TokenTypes.RBRACK)
            while func_tok is not None or func_tok2 is not None or func_tok3 is not None or func_tok4 is not None \
                    and func_tok5 is None:
                node1.add_child(self.parse_element())
                func_tok2 = self.match(TokenTypes.VARIABLE)
                if func_tok2 is None:
                    self.next_token()
                func_tok5 = self.match(TokenTypes.RBRACK)
                if func_tok5 is not None:
                    self.parselist()
                    return node1
            if func_tok5 is not None:
                self.parselist()
            return node1
        elif func_tok5 is None and ';' in \
                self.tokens[self.tok_index].text or ']' in self.tokens[self.tok_index].text:
            print("Expecting %s found %s at line %s" % (TokenTypes.names[TokenTypes.PARAMETER],
                                                        self.tokens[self.tok_index].text,
                                                        self.tokens[self.tok_index].linecount))
            exit(0)
        self.next_token()

    ###########################

    # MAIN                    #

    ###########################


def main():
    with open("script.txt", "r") as f:
        data = f.read()

    lexer = Lexer(data)
    tokens = lexer.next_token()
    # for tok in tokens:
    #    print(tok.__str__())
    parser = Parser(tokens)
    t = parser.parse_digraph()
    print(t.to_string_tree())


if __name__ == "__main__":
    sys.exit(main())
