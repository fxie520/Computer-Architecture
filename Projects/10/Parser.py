import re
from Utils import *


# Handles class statements which starts at tokens[start_pos + 1]. Governs all following handlers.
def class_handler(tokens: list, tag_list: list, position: int, output):
    output.write("<class>\n")

    position += 1
    assert tokens[position] == "class"
    output.write("<keyword> class </keyword>\n")

    position += 1
    output.write("<identifier> " + tokens[position] + " </identifier>\n")

    position += 1
    assert tokens[position] == "{"
    output.write("<symbol> { </symbol>\n")

    # Look ahead 1 token and determine the next handler to use
    while tokens[position + 1] in {"static", "field"}:
        position = class_var_dec_handler(tokens, tag_list, position, output)

    while tokens[position + 1] in {"constructor", "function", "method"}:
        position = subroutine_dec_handler(tokens, tag_list, position, output)

    position += 1
    assert tokens[position] == "}"
    output.write("<symbol> } </symbol>\n")

    output.write("</class>\n")
    return


def class_var_dec_handler(tokens: list, tag_list: list, position: int, output) -> int:
    output.write("<classVarDec>\n")

    position += 1
    assert tokens[position] in {"static", "field"}
    output.write("<keyword> " + tokens[position] + " </keyword>\n")

    # Type is either a keyword like int or an identifier (user defined type)
    position += 1
    if tokens[position] in keywords:
        output.write("<keyword> " + tokens[position] + " </keyword>\n")
    else:
        output.write("<identifier> " + tokens[position] + " </identifier>\n")

    position += 1
    output.write("<identifier> " + tokens[position] + " </identifier>\n")

    # Look ahead and see if multiple variables are declared
    while tokens[position + 1] == ",":
        position += 1
        output.write("<symbol> , </symbol>\n")

        position += 1
        output.write("<identifier> " + tokens[position] + " </identifier>\n")

    position += 1
    output.write("<symbol> ; </symbol>\n")

    output.write("</classVarDec>\n")
    return position


def subroutine_dec_handler(tokens: list, tag_list: list, position: int, output) -> int:
    output.write("<subroutineDec>\n")

    position += 1
    assert tokens[position] in {"constructor", "function", "method"}
    output.write("<keyword> " + tokens[position] + " </keyword>\n")

    position += 1
    if tokens[position] == "void":
        output.write("<keyword> void </keyword>\n")
    else:
        output.write("<identifier> " + tokens[position] + " </identifier>\n")

    position += 1
    output.write("<identifier> " + tokens[position] + " </identifier>\n")

    position += 1
    output.write("<symbol> ( </symbol>\n")

    if tokens[position + 1] != ")":
        position = parameter_list_handler(tokens, tag_list, position, output)
    # Write tags with no content between them
    else:
        output.write("<parameterList>\n")
        output.write("</parameterList>\n")

    position += 1
    output.write("<symbol> ) </symbol>\n")

    position = subroutine_body_handler(tokens, tag_list, position, output)

    output.write("</subroutineDec>\n")
    return position


def parameter_list_handler(tokens: list, tag_list: list, position: int, output) -> int:
    output.write("<parameterList>\n")

    position += 1
    if tokens[position] in keywords:
        output.write("<keyword> " + tokens[position] + " </keyword>\n")
    else:
        output.write("<identifier> " + tokens[position] + " </identifier>\n")

    position += 1
    output.write("<identifier> " + tokens[position] + " </identifier>\n")

    # Look ahead and see if multiple variables are declared
    while tokens[position + 1] == ",":
        position += 1
        output.write("<symbol> , </symbol>\n")

        position += 1
        if tokens[position] in keywords:
            output.write("<keyword> " + tokens[position] + " </keyword>\n")
        else:
            output.write("<identifier> " + tokens[position] + " </identifier>\n")

        position += 1
        output.write("<identifier> " + tokens[position] + " </identifier>\n")

    output.write("</parameterList>\n")
    return position


def subroutine_body_handler(tokens: list, tag_list: list, position: int, output) -> int:
    output.write("<subroutineBody>\n")

    position += 1
    assert tokens[position] == "{"
    output.write("<symbol> { </symbol>\n")

    # Look ahead and handles 0 or multiple variable declarations
    while tokens[position + 1] == "var":
        position = var_dec_handler(tokens, tag_list, position, output)

    position = statements_handler(tokens, tag_list, position, output)

    position += 1
    assert tokens[position] == "}"
    output.write("<symbol> } </symbol>\n")

    output.write("</subroutineBody>\n")
    return position


def var_dec_handler(tokens: list, tag_list: list, position: int, output) -> int:
    output.write("<varDec>\n")

    position += 1
    assert tokens[position] == "var"
    output.write("<keyword> var </keyword>\n")

    position += 1
    if tokens[position] in keywords:
        output.write("<keyword> " + tokens[position] + " </keyword>\n")
    else:
        output.write("<identifier> " + tokens[position] + " </identifier>\n")

    position += 1
    output.write("<identifier> " + tokens[position] + " </identifier>\n")

    # Look ahead and see if multiple variables are declared
    while tokens[position + 1] == ",":
        position += 1
        output.write("<symbol> , </symbol>\n")

        position += 1
        output.write("<identifier> " + tokens[position] + " </identifier>\n")

    position += 1
    output.write("<symbol> ; </symbol>\n")

    output.write("</varDec>\n")
    return position


def statements_handler(tokens: list, tag_list: list, position: int, output) -> int:
    output.write("<statements>\n")

    while tokens[position + 1] in {"let", "if", "while", "do", "return"}:
        if tokens[position + 1] == "let":
            position = let_statement_handler(tokens, tag_list, position, output)
        elif tokens[position + 1] == "if":
            position = if_statement_handler(tokens, tag_list, position, output)
        elif tokens[position + 1] == "while":
            position = while_statement_handler(tokens, tag_list, position, output)
        elif tokens[position + 1] == "do":
            position = do_statement_handler(tokens, tag_list, position, output)
        # Return statement
        else:
            position = return_statement_handler(tokens, tag_list, position, output)

    output.write("</statements>\n")
    return position


def let_statement_handler(tokens: list, tag_list: list, position: int, output) -> int:
    output.write("<letStatement>\n")

    position += 1
    output.write("<keyword> let </keyword>\n")

    position += 1
    output.write("<identifier> " + tokens[position] + " </identifier>\n")

    # Look ahead and see if "[expression]" follows
    if tokens[position + 1] == "[":
        position += 1
        output.write("<symbol> [ </symbol>\n")

        position = expression_handler(tokens, tag_list, position, output)

        position += 1
        assert tokens[position] == "]"
        output.write("<symbol> ] </symbol>\n")

    position += 1
    assert tokens[position] == "="
    output.write("<symbol> = </symbol>\n")

    position = expression_handler(tokens, tag_list, position, output)

    position += 1
    assert tokens[position] == ";"
    output.write("<symbol> ; </symbol>\n")

    output.write("</letStatement>\n")
    return position


def if_statement_handler(tokens: list, tag_list: list, position: int, output) -> int:
    output.write("<ifStatement>\n")

    position += 1
    output.write("<keyword> if </keyword>\n")

    position += 1
    assert tokens[position] == "("
    output.write("<symbol> ( </symbol>\n")

    position = expression_handler(tokens, tag_list, position, output)

    position += 1
    assert tokens[position] == ")"
    output.write("<symbol> ) </symbol>\n")

    position += 1
    assert tokens[position] == "{"
    output.write("<symbol> { </symbol>\n")

    position = statements_handler(tokens, tag_list, position, output)

    position += 1
    assert tokens[position] == "}"
    output.write("<symbol> } </symbol>\n")

    # Look ahead and see if an "(else {statements})" follows
    if tokens[position + 1] == "else":
        position += 1
        output.write("<keyword> else </keyword>\n")

        position += 1
        assert tokens[position] == "{"
        output.write("<symbol> { </symbol>\n")

        position = statements_handler(tokens, tag_list, position, output)

        position += 1
        assert tokens[position] == "}"
        output.write("<symbol> } </symbol>\n")

    output.write("</ifStatement>\n")
    return position


def while_statement_handler(tokens: list, tag_list: list, position: int, output) -> int:
    output.write("<whileStatement>\n")

    position += 1
    assert tokens[position] == "while"
    output.write("<keyword> while </keyword>\n")

    position += 1
    assert tokens[position] == "("
    output.write("<symbol> ( </symbol>\n")

    position = expression_handler(tokens, tag_list, position, output)

    position += 1
    assert tokens[position] == ")"
    output.write("<symbol> ) </symbol>\n")

    position += 1
    assert tokens[position] == "{"
    output.write("<symbol> { </symbol>\n")

    position = statements_handler(tokens, tag_list, position, output)

    position += 1
    assert tokens[position] == "}"
    output.write("<symbol> } </symbol>\n")

    output.write("</whileStatement>\n")
    return position


def do_statement_handler(tokens: list, tag_list: list, position: int, output) -> int:
    output.write("<doStatement>\n")

    position += 1
    assert tokens[position] == "do"
    output.write("<keyword> do </keyword>\n")

    position = subroutine_call_handler(tokens, tag_list, position, output)

    position += 1
    assert tokens[position] == ";"
    output.write("<symbol> ; </symbol>\n")

    output.write("</doStatement>\n")
    return position


def return_statement_handler(tokens: list, tag_list: list, position: int, output) -> int:
    output.write("<returnStatement>\n")

    position += 1
    assert tokens[position] == "return"
    output.write("<keyword> return </keyword>\n")

    # Look ahead and see if an expression follows
    if tokens[position + 1] != ";":
        position = expression_handler(tokens, tag_list, position, output)

    position += 1
    assert tokens[position] == ";"
    output.write("<symbol> ; </symbol>\n")

    output.write("</returnStatement>\n")
    return position


def subroutine_call_handler(tokens: list, tag_list: list, position: int, output) -> int:
    # Look ahead 2 positions to see if we are in the case "(class name | var name).subroutine name ..."
    if tokens[position + 2] == ".":
        position += 1
        output.write("<identifier> " + tokens[position] + " </identifier>\n")

        position += 1
        assert tokens[position] == "."
        output.write("<symbol> . </symbol>\n")

    position += 1
    output.write("<identifier> " + tokens[position] + " </identifier>\n")

    position += 1
    assert tokens[position] == "("
    output.write("<symbol> ( </symbol>\n")

    # Look ahead one position to see if an expression list follows
    if tokens[position + 1] != ")":
        position = expression_list_handler(tokens, tag_list, position, output)
    else:
        output.write("<expressionList>\n")
        output.write("</expressionList>\n")

    position += 1
    assert tokens[position] == ")"
    output.write("<symbol> ) </symbol>\n")
    return position


def expression_list_handler(tokens: list, tag_list: list, position: int, output) -> int:
    output.write("<expressionList>\n")

    position = expression_handler(tokens, tag_list, position, output)

    # Look ahead and see if multiple expressions present
    while tokens[position + 1] == ",":
        position += 1
        output.write("<symbol> , </symbol>\n")

        position = expression_handler(tokens, tag_list, position, output)

    output.write("</expressionList>\n")
    return position


def expression_handler(tokens: list, tag_list: list, position: int, output) -> int:
    output.write("<expression>\n")

    position = term_handler(tokens, tag_list, position, output)

    # Look ahead and see if multiple expressions present
    while tokens[position + 1] in operators:
        position += 1
        output.write("<symbol> " + tokens[position] + " </symbol>\n")

        position = term_handler(tokens, tag_list, position, output)

    output.write("</expression>\n")
    return position


def term_handler(tokens: list, tag_list: list, position: int, output) -> int:
    output.write("<term>\n")

    # Look ahead ... tokens to see which case we are in
    if tokens[position + 1].isnumeric():
        position += 1
        output.write("<integerConstant> " + tokens[position] + " </integerConstant>\n")
    elif tag_list[position + 1] == "stringConstant":
        position += 1
        output.write("<stringConstant> " + tokens[position] + " </stringConstant>\n")
    elif tokens[position + 1] in keyword_constants:
        position += 1
        output.write("<keyword> " + tokens[position] + " </keyword>\n")
    elif tokens[position + 1] == "(":
        position += 1
        output.write("<symbol> ( </symbol>\n")

        position = expression_handler(tokens, tag_list, position, output)

        position += 1
        assert tokens[position] == ")"
        output.write("<symbol> ) </symbol>\n")
    elif tokens[position + 1] in unary_operators:
        position += 1
        output.write("<symbol> " + tokens[position] + " </symbol>\n")

        position = term_handler(tokens, tag_list, position, output)
    # Look ahead 2 tokens
    elif tokens[position + 2] == "[":
        position += 1
        output.write("<identifier> " + tokens[position] + " </identifier>\n")

        position += 1
        output.write("<symbol> [ </symbol>\n")

        position = expression_handler(tokens, tag_list, position, output)

        position += 1
        assert tokens[position] == "]"
        output.write("<symbol> ] </symbol>\n")
    # Look ahead 2 tokens for subroutine call
    elif tokens[position + 2] in {".", "("}:
        position = subroutine_call_handler(tokens, tag_list, position, output)
    # var_name
    else:
        position += 1
        assert tag_list[position] == "identifier"
        output.write("<identifier> " + tokens[position] + " </identifier>\n")

    output.write("</term>\n")
    return position


# Driver code for debugging the parser only
if __name__ == '__main__':
    # temp_file = "./ArrayTest/Main_temp.xml"
    # out_file = "./ArrayTest/Main_out.xml"
    # temp_file = "./Square/Main_temp.xml"
    # out_file = "./Square/Main_out.xml"
    # temp_file = "./Square/Square_temp.xml"
    # out_file = "./Square/Square_out.xml"
    temp_file = "./Square/SquareGame_temp.xml"
    out_file = "./Square/SquareGame_out.xml"
    print(f"Temp XML file: {temp_file}")
    print(f"Output XML file: {out_file}")
    # Clear output file
    with open(out_file, "w") as _:
        pass

    lines = []
    tags = []
    with open(temp_file, "r") as f:
        # Retrieve the text content of XML
        for line in f:
            tag = re.findall("^<[^<>]+>", line)[0][1:-1]
            # Remove start tag
            line = re.sub("^<[^<>]+>[ ]*", "", line)
            # Remove end tag
            line = re.sub("[ ]*<[^<>]+>\n$", "", line)
            # Remove empty lines
            if line != "\n" and line != "":
                lines.append(line)
                assert tag in {"keyword", "identifier", "symbol", "stringConstant", "integerConstant"}
                tags.append(tag)
    print(lines)
    print(tags)

    pos = -1
    assert lines[pos + 1] == "class"
    with open(out_file, "a") as out_file:
        class_handler(lines, tags, pos, out_file)
