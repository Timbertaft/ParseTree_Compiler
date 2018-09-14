###########################

# IMPORTS                  #

###########################

import string

###########################

# STATES                #

###########################

BRACECOUNT = 0
DIGRAPHCOUNT = 0

###########################

# CONSTANTS                  #

###########################

LETTERS = string.ascii_letters
DIGITS = '0123456789'

###########################

# TOKEN                   #

###########################

IDENTIFIER = 'IDENTIFIER'
ID = 'ID'
LEFTBRACE = 'LEFTBRACE'
DIGRAPH = "digraph"


class Token(object):
    def __init__(self, typ, value):
        self.type = typ
        self.value = value


###########################

# LEXER                    #

###########################


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char is not None:
            if self.current_char.isspace():
                self.advance()
                continue

            elif self.current_char == '[':
                tokens.append(Token(ID, self.id()))

            elif self.current_char == '{':
                tokens.append(Token(LEFTBRACE, '{'))
                BRACECOUNT == 1

            elif self.current_char in LETTERS:
                tokens.append(Token(IDENTIFIER, self.identifier()))

            elif self.current_char in DIGRAPH:
                tokens.append(Token(DIGRAPH, self.digraph()))

        return tokens


    def id(self):
        id = ""
        self.advance()

        while self.current_char != ']':
            id += self.current_char
            self.advance()

        self.advance()
        return id

    def digraph(self):
        digraph = ""
        self.advance()

        while self.current_char in DIGRAPH:
            if digraph != "digraph":
                if BRACECOUNT == 0:
                    digraph += self.current_char
                    self.advance()

                elif digraph == "digraph":
                    DIGRAPHCOUNT == 1
                    self.advance()

    def identifier(self):
        result = ""

        while self.current_char in LETTERS + DIGITS:
            if BRACECOUNT == 1:
                if DIGRAPHCOUNT == 1:
                    result += self.current_char
                    self.advance()

        return result


    ###########################

    # MAIN                    #

    ###########################


with open("script.txt", "r") as f:
    data = f.read()

lexer = Lexer(data)
tokens = lexer.make_tokens()

for tok in tokens:
    print("Type:", tok.type)
    print("Value:", tok.value)
