keyword = {"class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void",
           "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"}

# It is necessary to check the existence of ";" then "&" then other symbols, in the tokenizer.
# So symbols is an array instead of a set.
symbols = [";", "&", "{", "}", "(", ")", "[", "]", ".", ",", "+", "-", "*", "/", "|", "<", ">", "=", "~"]

xml_symbols = {"&lt;", "&gt;", "&amp;", "&quot;"}




