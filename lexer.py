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
                pval = Token(TokenTypes.PARAMETER, parametervalue, linecount)
                tokens.append(pval)

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

    def consume(self, tok_type):
        tok = self.tokens[self.tok_index]

        if tok.type == tok_type:
            return tok

        self.tok_index += 1

    def parse(self):
        self.program()

    def program(self):
        self.statements()

    #def node_list(self):
     #   node = self.node_list_elements()
      #  return node

    # def node_list_elements(self):

    def statements(self):

        self.tok_index = 0
        bracevalue = 0
        while self.tok_index < len(self.tokens):
            if bracevalue == 0:
                func_tok = self.consume(TokenTypes.LBRACE)
                if func_tok is not None and func_tok.text == '{':
                    bracevalue = 1

            if bracevalue == 1:
                func_tok = self.consume(TokenTypes.RBRACE)
                if func_tok is None and self.tokens[self.tok_index].type == TokenTypes.EOF:
                    print("Expecting %s found %s at %s" % (TokenTypes.names[TokenTypes.RBRACE],
                                                           self.tokens[self.tok_index].text,
                                                           self.tokens[self.tok_index].linecount))
                    break
                elif func_tok is not None:
                    bracevalue = 0

        self.tok_index = 0
        lbrack = 0

        while self.tok_index < len(self.tokens):
            if lbrack == 0:
                func_tok = self.consume(TokenTypes.LBRACK)
                if func_tok is not None and func_tok.text == '[':
                    lbrack = 1
            if lbrack == 1:
                func_tok = self.consume(TokenTypes.RBRACK)
                if func_tok is None and ';' in self.tokens[self.tok_index].text:
                    print("Expecting %s found %s at line %s" % (TokenTypes.names[TokenTypes.RBRACK],
                                                                self.tokens[self.tok_index].text,
                                                                self.tokens[self.tok_index].linecount))
                    exit(0)
                elif func_tok is not None:
                    node = AST("list")
                    self.node = node
                    lbrack = 0

        self.tok_index = 0
        connectionvalue = 0
        while self.tok_index < len(self.tokens):
            if connectionvalue == 0:
                func_tok = self.consume(TokenTypes.CONNECTION)
                if func_tok is not None and func_tok.text == '->':
                    connectionvalue = 1
            if connectionvalue == 1:
                func_tok = self.consume(TokenTypes.ID)
                if func_tok is None and '[' in self.tokens[self.tok_index].text:
                    print("Expecting %s found %s at line %s" % (TokenTypes.names[TokenTypes.ID],
                                                                self.tokens[self.tok_index].text,
                                                                self.tokens[self.tok_index].linecount))
                    exit(0)
                elif func_tok is not None:
                    connectionvalue = 0

        self.tok_index = 0
        variablevalue = 0
        while self.tok_index < len(self.tokens):
            if variablevalue == 0:
                func_tok = self.consume(TokenTypes.VARIABLE)
                if func_tok is not None:
                    variablevalue = 1
            if variablevalue == 1:
                func_tok = self.consume(TokenTypes.ASSIGNMENT)
                if func_tok is None and ']' in self.tokens[self.tok_index].text or ';' in self.tokens[
                    self.tok_index].text:
                    print("Expecting %s found %s at line %s" % (TokenTypes.names[TokenTypes.ASSIGNMENT],
                                                                self.tokens[self.tok_index].text,
                                                                self.tokens[self.tok_index].linecount))
                    exit(0)
                elif func_tok is not None:
                    variablevalue = 0

        self.tok_index = 0
        equationvalue = 0
        while self.tok_index < len(self.tokens):
            if equationvalue == 0:
                func_tok = self.consume(TokenTypes.EQUATION)
                if func_tok is not None:
                    sub_node = AST(func_tok)
                    node.add_child(sub_node)
                elif func_tok is None and ']' in self.tokens[self.tok_index].text or ';' in self.tokens[
                        self.tok_index].text:
                        print("Expecting %s found %s at line %s" % (TokenTypes.names[TokenTypes.ASSIGNMENT],
                                                                    self.tokens[self.tok_index].text,
                                                                    self.tokens[self.tok_index].linecount))
                exit(0)

    ###########################

    # MAIN                    #

    ###########################


def main():
    with open("script.txt", "r") as f:
        data = f.read()

    lexer = Lexer(data)
    tokens = lexer.next_token()
    for tok in tokens:
        print(tok.__str__())
    parser = Parser(tokens)
    parser.parse()



if __name__ == "__main__":
    sys.exit(main())
