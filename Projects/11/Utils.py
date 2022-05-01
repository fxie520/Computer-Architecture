keywords = {"class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void",
            "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"}

# It is necessary to check the existence of ";" then "&" then other symbols, in the tokenizer.
# So symbols is an array instead of a set.
symbols = [";", "&", "{", "}", "(", ")", "[", "]", ".", ",", "+", "-", "*", "/", "|", "<", ">", "=", "~"]

xml_symbols = {"&lt;", "&gt;", "&amp;", "&quot;"}

# Syntax = operator: corresponding vm code
operators = {
    "+": "add",
    "-": "sub",
    "*": "call Math.multiply 2",
    "/": "call Math.divide 2",
    "|": "or",
    "<": "lt",
    ">": "gt",
    "&lt;": "lt",
    "&gt;": "gt",
    "&amp;": "and",
    "=": "eq",
}

# Syntax = unary operator: corresponding vm code
unary_operators = {
    "-": "neg",
    "~": "not",
}

# Syntax = keyword_constant: corresponding vm code
keyword_constants = {"true": "push constant 1\nneg", "false": "push constant 0",
                     "null": "push constant 0", "this": "push pointer 0"}
