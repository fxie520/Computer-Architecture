import re


# Handles class statements which starts at tokens[start_pos + 1]
def class_handler(tokens: list, position: int, output) -> int:
    with open(output, "a") as f_out:
        position += 1
        assert tokens[position] == "class"
        f_out.write("<keyword> class </keyword>\n")

        position += 1
        f_out.write("<identifier> " + tokens[position] + " </identifier>\n")

        position += 1
        assert tokens[position] == "{"
        f_out.write("<symbol> { </symbol>\n")

        # Look ahead 1 token and determine the next handler to use
        while tokens[position + 1] in {"static", "field"}:
            position = class_var_dec_handler(tokens, position, output)

        while tokens[position + 1] in {"constructor", "function", "method"}:
            position = subroutine_dec_handler(tokens, position, output)

        position += 1
        assert tokens[position] == "}"
        f_out.write("<symbol> } </symbol>\n")
    return position


def class_var_dec_handler(tokens: list, position: int, output) -> int:
    with open(output, "a") as f_out:
        position += 1
        assert tokens[position] in {"static", "field"}
        f_out.write("<keyword>" + tokens[position] + "</keyword>\n")

        position += 1
        f_out.write("<identifier>" + tokens[position] + "</identifier>\n")

        position += 1
        f_out.write("<identifier>" + tokens[position] + "</identifier>\n")

        # Look ahead and see if multiple variables are declared
        while tokens[position + 1] == ",":
            position += 1
            f_out.write("<symbol> , </symbol>\n")

            position += 1
            f_out.write("<identifier>" + tokens[position] + "</identifier>\n")

        position += 1
        f_out.write("<symbol> ; </symbol>\n")
    return position


def subroutine_dec_handler(tokens: list, position: int, output) -> int:
    with open(output, "a") as f_out:
        position += 1
        assert tokens[position] in {"static", "field"}
        f_out.write("<keyword>" + tokens[position] + "</keyword>\n")

        position += 1
        f_out.write("<keyword>" + tokens[position] + "</keyword>\n")

        position += 1
        f_out.write("<identifier>" + tokens[position] + "</identifier>\n")

        position += 1
        f_out.write("<symbol> ( </symbol>\n")

        if tokens[position + 1] != ")":
            position = parameter_list_handler(tokens, position, output)

        position += 1
        f_out.write("<symbol> ) </symbol>\n")

        position = subroutine_body_handler(tokens, position, output)
    return position


def parameter_list_handler(tokens: list, position: int, output) -> int:
    with open(output, "a") as f_out:
        position += 1
        f_out.write("<identifier>" + tokens[position] + "</identifier>\n")

        position += 1
        f_out.write("<identifier>" + tokens[position] + "</identifier>\n")

        # Look ahead and see if multiple variables are declared
        while tokens[position + 1] == ",":
            position += 1
            f_out.write("<symbol> , </symbol>\n")

            position += 1
            f_out.write("<identifier>" + tokens[position] + "</identifier>\n")

            position += 1
            f_out.write("<identifier>" + tokens[position] + "</identifier>\n")
    return position


def subroutine_body_handler(tokens: list, position: int, output) -> int:
    with open(output, "a") as f_out:
        position += 1
        assert tokens[position] == "{"
        f_out.write("<symbol> { </symbol>\n")

        # Look ahead and handles 0 or multiple variable declarations
        while tokens[position + 1] == "var":
            position = var_dec_handler(tokens, position, output)

        position = statements_handler(tokens, position, output)

        position += 1
        assert tokens[position] == "}"
        f_out.write("<symbol> } </symbol>\n")
    return position


def var_dec_handler(tokens: list, position: int, output) -> int:
    with open(output, "a") as f_out:
        position += 1
        assert tokens[position] == "var"
        f_out.write("<keyword> var </keyword>\n")

        position += 1
        f_out.write("<identifier>" + tokens[position] + "</identifier>\n")

        position += 1
        f_out.write("<identifier>" + tokens[position] + "</identifier>\n")

        # Look ahead and see if multiple variables are declared
        while tokens[position + 1] == ",":
            position += 1
            f_out.write("<symbol> , </symbol>\n")

            position += 1
            f_out.write("<identifier>" + tokens[position] + "</identifier>\n")

        position += 1
        f_out.write("<symbol> ; </symbol>\n")
    return position


def statements_handler(tokens: list, position: int, output) -> int:
    with open(output, "a") as f_out:
        while tokens[position + 1] in {"let", "if", "while", "do", "return"}:
            if tokens[position + 1] == "let":
                position = let_statement_handler(tokens, position, output)
            elif tokens[position + 1] == "if":
                position = if_statement_handler(tokens, position, output)
            elif tokens[position + 1] == "while":
                position = while_statement_handler(tokens, position, output)
            elif tokens[position + 1] == "do":
                position = do_statement_handler(tokens, position, output)
            # Return statement
            else:
                position = return_statement_handler(tokens, position, output)
    return position


def let_statement_handler(tokens: list, position: int, output) -> int:
    with open(output, "a") as f_out:
        position += 1
        f_out.write("<keyword> let </keyword>\n")

        position += 1
        f_out.write("<identifier> " + tokens[position] + " </identifier>\n")

        # Look ahead and see if "[expression]" follows
        if tokens[position + 1] == "[":
            position += 1
            f_out.write("<symbol> [ </symbol>\n")

            # TODO: expression

            position += 1
            assert tokens[position] == "]"
            f_out.write("<symbol> ] </symbol>\n")

        position += 1
        assert tokens[position] == "="
        f_out.write("<symbol> = </symbol>\n")

        # TODO: expression

        position += 1
        assert tokens[position] == ";"
        f_out.write("<symbol> ; </symbol>\n")
    return position


def if_statement_handler(tokens: list, position: int, output) -> int:
    with open(output, "a") as f_out:
        position += 1
        f_out.write("<keyword> if </keyword>\n")

        position += 1
        assert tokens[position] == "("
        f_out.write("<symbol> ( </symbol>\n")

        # TODO: expression

        position += 1
        assert tokens[position] == ")"
        f_out.write("<symbol> ) </symbol>\n")

        position += 1
        assert tokens[position] == "{"
        f_out.write("<symbol> { </symbol>\n")

        position = statements_handler(tokens, position, output)

        position += 1
        assert tokens[position] == "}"
        f_out.write("<symbol> } </symbol>\n")

        # Look ahead and see if an "(else {statements})" follows
        if tokens[position + 1] == "(":
            position += 1
            f_out.write("<symbol> ( </symbol>\n")

            position += 1
            assert tokens[position] == "else"
            f_out.write("<keyword> else </keyword>\n")

            position += 1
            assert tokens[position] == "{"
            f_out.write("<symbol> { </symbol>\n")

            position = statements_handler(tokens, position, output)

            position += 1
            assert tokens[position] == "}"
            f_out.write("<symbol> } </symbol>\n")

            position += 1
            assert tokens[position] == ")"
            f_out.write("<symbol> ) </symbol>\n")
    return position


def while_statement_handler(tokens: list, position: int, output) -> int:
    with open(output, "a") as f_out:
        position += 1
        assert tokens[position] == "while"
        f_out.write("<keyword> while </keyword>\n")

        position += 1
        assert tokens[position] == "("
        f_out.write("<symbol> ( </symbol>\n")

        # TODO: expression

        position += 1
        assert tokens[position] == ")"
        f_out.write("<symbol> ) </symbol>\n")

        position += 1
        assert tokens[position] == "{"
        f_out.write("<symbol> { </symbol>\n")

        position = statements_handler(tokens, position, output)

        position += 1
        assert tokens[position] == "}"
        f_out.write("<symbol> } </symbol>\n")
    return position


def do_statement_handler(tokens: list, position: int, output) -> int:
    with open(output, "a") as f_out:
        position += 1
        assert tokens[position] == "do"
        f_out.write("<keyword> do </keyword>\n")

        # TODO: subroutine call

        position += 1
        assert tokens[position] == ";"
        f_out.write("<symbol> ; </symbol>\n")
    return position


def return_statement_handler(tokens: list, position: int, output) -> int:
    with open(output, "a") as f_out:
        position += 1
        assert tokens[position] == "return"
        f_out.write("<keyword> return </keyword>\n")

        # Look ahead and see if an expression follows
        if tokens[position + 1] != ";":
            # TODO: expression
            pass

        position += 1
        assert tokens[position] == ";"
        f_out.write("<symbol> ; </symbol>\n")
    return position


def subroutine_call_handler(tokens: list, position: int, output) -> int:
    return position


def expression_handler(tokens: list, position: int, output) -> int:
    return position


# Driver code for debugging the parser only
if __name__ == '__main__':
    temp_file = "./ArrayTest/Main_temp.xml"
    out_file = "./ArrayTest/Main_out.xml"
    print(f"Temp XML file: {temp_file}")
    print(f"Output XML file: {out_file}")

    lines = []
    with open(temp_file, "r") as f:
        # Retrieve the text content of XML
        for line in f:
            # Remove start tag
            line = re.sub("^<[^<>]+>[ ]*", "", line)
            # Remove end tag
            line = re.sub("[ ]*<[^<>]+>\n$", "", line)
            # Remove empty lines
            if line != "\n" and line != "":
                lines.append(line)
    print(lines)

    pos = 0
