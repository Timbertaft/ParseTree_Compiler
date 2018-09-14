# ParseTree_Compiler
Compiler for DOT Diagraming Grammar complete with lexer and parser coded in Python

This repo contains the contents described above.
Parser: is a top-down recursive descent parser that separates the values from an example piece of DOT code and splits it into its containing elements using brackets.  The number included represents the line in which the token occurs with the first word showing which label the token is referencing.

Lexer: An initial dummy lexer to confirm functionality.  Lexer incorporated into parser functionality included in the parser.py file.

ParseLark: removes unnecessary additional information from the original parser and outputs information into a tabed and organized parse tree representing order of layers within the parsing structure in a clean parse tree.

Cycle Checker: Adds minor included functionality for identifying the cyclomatic complexity value of the values outputted by the parse tree.
