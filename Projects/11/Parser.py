import re
from Utils import *
from SymbolTable import SymbolTable


# Initialization of global variables
class_symbol_table = SymbolTable()
subroutine_symbol_table = SymbolTable()
class_var_kind = ""  # field/static variable
class_var_type = ""  # int, char, boolean or user-defined type
class_var_name = ""
class_name = ""  # Used for function naming in vm code (i.e. class_name.function_name)
subroutine_name = ""
subroutine_kind = ""  # constructor, function or method
subroutine_type = ""  # void, int, char, boolean or user-defined type
label_counter = 0  # Used for handling flow of control (i.e. if/while)


# Write VM code for the entire class which starts at tokens[start_pos + 1]. Governs all following handlers.
def class_handler(tokens: list, tag_list: list, position: int, output):
    # Reset class-level symbol table
    global class_symbol_table
    class_symbol_table.reset()

    # "class"
    position += 1
    assert tokens[position] == "class"

    # class name
    position += 1
    global class_name
    class_name = tokens[position]

    # "{"
    position += 1
    assert tokens[position] == "{"

    # Class-level variable declarations: look ahead 1 token and determine the next handler to use
    while tokens[position + 1] in {"static", "field"}:
        position = class_var_dec_handler(tokens, position)

    # Subroutines
    while tokens[position + 1] in {"constructor", "function", "method"}:
        position = subroutine_dec_handler(tokens, tag_list, position, output)

    # "}"
    position += 1
    assert tokens[position] == "}"
    return


# Write VM code for class-level variable (i.e. static or field variables) declarations
def class_var_dec_handler(tokens: list, position: int) -> int:
    # "static" or "field"
    position += 1
    assert tokens[position] in {"static", "field"}
    global class_var_kind
    class_var_kind = tokens[position]

    # Type is either a keyword like int or an identifier (user defined type)
    position += 1
    global class_var_type
    class_var_type = tokens[position]

    # Variable name
    position += 1
    global class_var_name
    class_var_name = tokens[position]

    # Add class-level variable to symbol table
    class_symbol_table.add_var(class_var_name, class_var_type, class_var_kind)

    # Look ahead and see if multiple variables are declared
    while tokens[position + 1] == ",":
        # ","
        position += 1

        # Variable name
        position += 1
        class_var_name = tokens[position]

        # Add class-level variable to symbol table
        class_symbol_table.add_var(class_var_name, class_var_type, class_var_kind)

    # ";"
    position += 1
    return position


# Write VM code for the entire subroutine
def subroutine_dec_handler(tokens: list, tag_list: list, position: int, output) -> int:
    # Initialize a new subroutine-level symbol table
    global subroutine_symbol_table, subroutine_name, subroutine_type, subroutine_kind
    subroutine_symbol_table.reset()

    # Constructor/function/method
    position += 1
    assert tokens[position] in {"constructor", "function", "method"}
    subroutine_kind = tokens[position]

    # Subroutine type
    position += 1
    subroutine_type = tokens[position]

    # Subroutine name
    position += 1
    subroutine_name = tokens[position]

    # "("
    position += 1

    # Add the first (implicit) argument to the subroutine-level symbol table if the subroutine is a method
    if subroutine_kind == "method":
        subroutine_symbol_table.add_var(var_name="this", var_type=subroutine_type, var_kind="argument")

    # Parameter list
    if tokens[position + 1] != ")":
        position = parameter_list_handler(tokens, position)

    # ")"
    position += 1

    position = subroutine_body_handler(tokens, tag_list, position, output)
    return position


# Add subroutine arguments to symbol table
def parameter_list_handler(tokens: list, position: int) -> int:
    subroutine_var_kind = "argument"

    # Variable type
    position += 1
    subroutine_var_type = tokens[position]

    # Variable name
    position += 1
    subroutine_var_name = tokens[position]

    # Add subroutine-level variable to symbol table
    global subroutine_symbol_table
    subroutine_symbol_table.add_var(subroutine_var_name, subroutine_var_type, subroutine_var_kind)

    # Look ahead and see if multiple variables are declared
    while tokens[position + 1] == ",":
        # ","
        position += 1

        # Variable type
        position += 1
        subroutine_var_type = tokens[position]

        # Variable name
        position += 1
        subroutine_var_name = tokens[position]

        # Add subroutine-level variable to symbol table
        subroutine_symbol_table.add_var(subroutine_var_name, subroutine_var_type, subroutine_var_kind)
    return position


# Write VM code for everything except the arguments in the subroutine
def subroutine_body_handler(tokens: list, tag_list: list, position: int, output) -> int:
    # "{"
    position += 1
    assert tokens[position] == "{"

    # Look ahead and handles 0 or multiple variable declarations
    n_vars = 0  # Number of local variables of the subroutine
    while tokens[position + 1] == "var":
        position = var_dec_handler(tokens, position)
    global subroutine_symbol_table
    n_vars += subroutine_symbol_table.local_var_counter

    # VM code for subroutine initialization
    output.write(f"function {class_name}.{subroutine_name} {n_vars}\n")
    # Number of 16-bit words required
    global subroutine_kind
    # For constructor declaration: make the OS allocate memory required for the instance,
    # then set "this" to be the address of the memory just allocated
    if subroutine_kind == "constructor":
        output.write(f"push constant {class_symbol_table.field_var_counter}\n")
        output.write("call Memory.alloc 1\n")
        output.write("pop pointer 0\n")
    # For method declaration: set "this" to be the first (implicit) argument
    elif subroutine_kind == "method":
        output.write("push argument 0\n")
        output.write("pop pointer 0\n")

    position = statements_handler(tokens, tag_list, position, output)

    # "}"
    position += 1
    assert tokens[position] == "}"
    return position


# Add local (subroutine-level) variable declaration to symbol table
def var_dec_handler(tokens: list, position: int) -> (int, int):
    global subroutine_symbol_table

    # "var"
    position += 1
    assert tokens[position] == "var"
    subroutine_var_kind = "local"

    # Variable type
    position += 1
    subroutine_var_type = tokens[position]

    # Variable name
    position += 1
    subroutine_var_name = tokens[position]

    # Add subroutine variable to symbol table
    subroutine_symbol_table.add_var(subroutine_var_name, subroutine_var_type, subroutine_var_kind)

    # Look ahead and see if multiple variables are declared
    while tokens[position + 1] == ",":
        # ","
        position += 1

        # Variable name
        position += 1
        subroutine_var_name = tokens[position]

        # Add subroutine variable to symbol table
        subroutine_symbol_table.add_var(subroutine_var_name, subroutine_var_type, subroutine_var_kind)

    # ";"
    position += 1
    return position


# Write VM code for statements
def statements_handler(tokens: list, tag_list: list, position: int, output) -> int:
    while tokens[position + 1] in {"let", "if", "while", "do", "return"}:
        if tokens[position + 1] == "let":
            position = let_statement_handler(tokens, tag_list, position, output)
        elif tokens[position + 1] == "if":
            position = if_statement_handler(tokens, tag_list, position, output)
        elif tokens[position + 1] == "while":
            position = while_statement_handler(tokens, tag_list, position, output)
        elif tokens[position + 1] == "do":
            position = do_statement_handler(tokens, tag_list, position, output)
        else:  # Return statement
            position = return_statement_handler(tokens, tag_list, position, output)
    return position


def let_statement_handler(tokens: list, tag_list: list, position: int, output) -> int:
    # "let"
    position += 1

    # Variable name
    position += 1
    var_name = tokens[position]

    # Lookup variable in class-level then subroutine-level symbol tables
    global subroutine_symbol_table, class_symbol_table
    if var_name in class_symbol_table.symbol_table:
        var_type = class_symbol_table.symbol_table[var_name]["type"]
        var_kind = class_symbol_table.symbol_table[var_name]["kind"]
        var_count = class_symbol_table.symbol_table[var_name]["count"]
    elif var_name in subroutine_symbol_table.symbol_table:
        var_type = subroutine_symbol_table.symbol_table[var_name]["type"]
        var_kind = subroutine_symbol_table.symbol_table[var_name]["kind"]
        var_count = subroutine_symbol_table.symbol_table[var_name]["count"]
    else:
        raise Exception("Variable in neither class-level nor subroutine-level symbol table")

    # Look ahead and see if "[expression]" follows, i.e. variable above is an array
    array_element_access = False
    if tokens[position + 1] == "[":
        array_element_access = True

        assert var_type == "Array"
        if var_kind == "field":
            output.write(f"push this {var_count}\n")
        else:
            output.write(f"push {var_kind} {var_count}\n")

        # "["
        position += 1

        # Expression
        position = expression_handler(tokens, tag_list, position, output)

        # "]"
        position += 1
        assert tokens[position] == "]"

        output.write("add\n")

    # "="
    position += 1
    assert tokens[position] == "="

    # Expression
    position = expression_handler(tokens, tag_list, position, output)

    if array_element_access:
        output.write("pop temp 0\n")
        output.write("pop pointer 1\n")
        output.write("push temp 0\n")
        output.write("pop that 0\n")
    else:
        if var_kind == "field":
            output.write(f"pop this {var_count}\n")
        else:
            output.write(f"pop {var_kind} {var_count}\n")

    # ";"
    position += 1
    assert tokens[position] == ";"
    return position


def if_statement_handler(tokens: list, tag_list: list, position: int, output) -> int:
    # Update label_counter
    global label_counter
    local_label_counter = label_counter
    label_counter += 2

    # "if"
    position += 1

    # "("
    position += 1
    assert tokens[position] == "("

    position = expression_handler(tokens, tag_list, position, output)
    output.write("not\n")
    output.write(f"if-goto label{local_label_counter + 1}\n")

    # ")"
    position += 1
    assert tokens[position] == ")"

    # "{"
    position += 1
    assert tokens[position] == "{"

    position = statements_handler(tokens, tag_list, position, output)

    # "}"
    position += 1
    assert tokens[position] == "}"

    # Look ahead and see if an "(else {statements})" follows
    else_statement = False
    if tokens[position + 1] == "else":
        else_statement = True
        output.write(f"goto label{local_label_counter + 2}\n")

        # "else"
        position += 1

        # "{"
        position += 1
        assert tokens[position] == "{"

    output.write(f"label label{local_label_counter + 1}\n")

    # Continue previous if block or not
    if else_statement:
        position = statements_handler(tokens, tag_list, position, output)

        # "}"
        position += 1
        assert tokens[position] == "}"

        output.write(f"label label{local_label_counter + 2}\n")
    return position


def while_statement_handler(tokens: list, tag_list: list, position: int, output) -> int:
    # Update label_counter
    global label_counter
    local_label_counter = label_counter
    label_counter += 2

    # "while"
    position += 1
    assert tokens[position] == "while"

    # "("
    position += 1
    assert tokens[position] == "("

    output.write(f"label label{local_label_counter + 1}\n")
    position = expression_handler(tokens, tag_list, position, output)
    output.write("not\n")
    output.write(f"if-goto label{local_label_counter + 2}\n")

    # ")"
    position += 1
    assert tokens[position] == ")"

    # "{"
    position += 1
    assert tokens[position] == "{"

    position = statements_handler(tokens, tag_list, position, output)
    output.write(f"goto label{local_label_counter + 1}\n")
    output.write(f"label label{local_label_counter + 2}\n")

    # "}"
    position += 1
    assert tokens[position] == "}"
    return position


def do_statement_handler(tokens: list, tag_list: list, position: int, output) -> int:
    # "do"
    position += 1
    assert tokens[position] == "do"

    position = subroutine_call_handler(tokens, tag_list, position, output)
    # "do some_subroutine" implies that the subroutine is void typed
    # Here the (useless) return value of a void method is discarded
    output.write("pop temp 0\n")

    # ";"
    position += 1
    assert tokens[position] == ";"
    return position


def return_statement_handler(tokens: list, tag_list: list, position: int, output) -> int:
    # "return"
    position += 1
    assert tokens[position] == "return"

    # Look ahead and see if an expression follows
    if tokens[position + 1] != ";":
        position = expression_handler(tokens, tag_list, position, output)
    # If not the subroutine must be either constructor or of type void
    elif subroutine_kind == "constructor":
        output.write("push pointer 0\n")
    elif subroutine_type == "void":
        output.write("push constant 0\n")
    else:
        raise Exception

    output.write("return\n")

    # ";"
    position += 1
    assert tokens[position] == ";"
    return position


# Write VM code for subroutine calls
def subroutine_call_handler(tokens: list, tag_list: list, position: int, output) -> int:
    # Name of the class that the called subroutine (not the current subroutine under compilation) belongs to
    called_subroutine_class_name = class_name

    # Look ahead 2 positions to see if we are in the case "(class name | var name).subroutine name ..."
    # Note: class_name.subroutine_name implies that the subroutine called is a function or constructor
    # Note: var_name.subroutine_name implies that the subroutine called is a method
    # Note: subroutine_name implies that the subroutine called is a method
    is_method = True
    if tokens[position + 2] == ".":
        # class name or variable name
        position += 1
        class_or_var_name = tokens[position]

        # Lookup the previous name in the symbol tables to see if it's a variable's name or a class's name
        if class_or_var_name in class_symbol_table.symbol_table:
            called_subroutine_class_name = class_symbol_table.symbol_table[class_or_var_name]["type"]
            var_kind = class_symbol_table.symbol_table[class_or_var_name]["kind"]
            var_count = class_symbol_table.symbol_table[class_or_var_name]["count"]
            if var_kind == "field":
                output.write(f"push this {var_count}\n")
            else:
                output.write(f"push {var_kind} {var_count}\n")
        elif class_or_var_name in subroutine_symbol_table.symbol_table:
            called_subroutine_class_name = subroutine_symbol_table.symbol_table[class_or_var_name]["type"]
            var_kind = subroutine_symbol_table.symbol_table[class_or_var_name]["kind"]
            var_count = subroutine_symbol_table.symbol_table[class_or_var_name]["count"]
            if var_kind == "field":
                output.write(f"push this {var_count}\n")
            else:
                output.write(f"push {var_kind} {var_count}\n")
        # class_or_var_name is a class's name
        else:
            is_method = False
            called_subroutine_class_name = class_or_var_name

        # "."
        position += 1
        assert tokens[position] == "."
    # subroutine_name
    else:
        output.write("push pointer 0\n")

    # Called subroutine name (not the name of the current subroutine under compilation)
    position += 1
    called_subroutine_name = tokens[position]

    # "("
    position += 1
    assert tokens[position] == "("

    # Look ahead one position to see if an expression list follows
    if tokens[position + 1] != ")":
        position, n_args = expression_list_handler(tokens, tag_list, position, output)
    else:
        n_args = 0

    # Add implicit argument if the subroutine is a method
    if is_method:
        n_args += 1

    # ")"
    position += 1
    assert tokens[position] == ")"

    # Write VM code
    output.write(f"call {called_subroutine_class_name}.{called_subroutine_name} {n_args}\n")
    return position


# Push values of expressions one by one (in order) on stack top
def expression_list_handler(tokens: list, tag_list: list, position: int, output) -> (int, int):
    # Number of expressions, which is the number of arguments of the subroutine call
    # in which the expression list presents
    n_args = 1
    position = expression_handler(tokens, tag_list, position, output)

    # Look ahead and see if multiple expressions present
    while tokens[position + 1] == ",":
        # ","
        position += 1

        n_args += 1
        position = expression_handler(tokens, tag_list, position, output)
    return position, n_args


# Push value of the evaluated expression on stack top
def expression_handler(tokens: list, tag_list: list, position: int, output) -> int:
    position = term_handler(tokens, tag_list, position, output)

    # Look ahead and see if multiple expressions present
    while tokens[position + 1] in operators:
        # Operator
        position += 1
        operator = tokens[position]

        position = term_handler(tokens, tag_list, position, output)

        # Write VM code
        output.write(f"{operators[operator]}\n")
    return position


# Push term value on stack top
def term_handler(tokens: list, tag_list: list, position: int, output) -> int:
    global subroutine_symbol_table, class_symbol_table

    # Look ahead 1 or 2 tokens to see which case we are in
    # Integer constant
    if tokens[position + 1].isnumeric():
        position += 1
        output.write(f"push constant {tokens[position]}\n")
    # String constant
    elif tag_list[position + 1] == "stringConstant":
        position += 1
        output.write(f"push constant {len(tokens[position])}\n")
        output.write("call String.new 1\n")
        for char in tokens[position]:
            # Convert character to integer according to ASCII
            # (the keyboard memory map used in NandToTetris is a part of the ASCII mapping)
            output.write(f"push constant {ord(char)}\n")
            output.write("call String.appendChar 2\n")
    # Keyword constant, i.e. "true", "false", "null" or "this"
    elif tokens[position + 1] in keyword_constants:
        position += 1
        keyword_constant = tokens[position]
        output.write(f"{keyword_constants[keyword_constant]}\n")
    # (expression)
    elif tokens[position + 1] == "(":
        # "("
        position += 1

        position = expression_handler(tokens, tag_list, position, output)

        # ")"
        position += 1
        assert tokens[position] == ")"
    # unaryOp (-, ~ or <) term
    elif tokens[position + 1] in unary_operators:
        # Unary operator
        position += 1
        unary_operator = tokens[position]

        position = term_handler(tokens, tag_list, position, output)

        # Write unary operator to VM code
        output.write(f"{unary_operators[unary_operator]}\n")
    # var_name[expression]
    elif tokens[position + 2] == "[":
        # Variable name
        position += 1
        var_name = tokens[position]

        # Lookup variable in class-level then subroutine-level symbol tables
        if var_name in class_symbol_table.symbol_table:
            var_kind = class_symbol_table.symbol_table[var_name]["kind"]
            var_count = class_symbol_table.symbol_table[var_name]["count"]
        elif var_name in subroutine_symbol_table.symbol_table:
            var_kind = subroutine_symbol_table.symbol_table[var_name]["kind"]
            var_count = subroutine_symbol_table.symbol_table[var_name]["count"]
        else:
            raise Exception("Variable in neither class-level nor subroutine-level symbol table")
        if var_kind == "field":
            output.write(f"push this {var_count}\n")
        else:
            output.write(f"push {var_kind} {var_count}\n")

        # "["
        position += 1

        position = expression_handler(tokens, tag_list, position, output)

        # Write VM code
        output.write("add\n")
        output.write("pop pointer 1\n")
        output.write(f"push that 0\n")

        # "]"
        position += 1
        assert tokens[position] == "]"
    # Subroutine call
    elif tokens[position + 2] in {".", "("}:
        position = subroutine_call_handler(tokens, tag_list, position, output)
    # Variable name
    else:
        position += 1
        assert tag_list[position] == "identifier"
        var_name = tokens[position]
        # Lookup variable in class-level then subroutine-level symbol tables
        if var_name in class_symbol_table.symbol_table:
            var_kind = class_symbol_table.symbol_table[var_name]["kind"]
            var_count = class_symbol_table.symbol_table[var_name]["count"]
        elif var_name in subroutine_symbol_table.symbol_table:
            var_kind = subroutine_symbol_table.symbol_table[var_name]["kind"]
            var_count = subroutine_symbol_table.symbol_table[var_name]["count"]
        else:
            raise Exception("Variable in neither class-level nor subroutine-level symbol table")
        # Write VM code
        if var_kind == "field":
            output.write(f"push this {var_count}\n")
        else:
            output.write(f"push {var_kind} {var_count}\n")
    return position


# Driver code for debugging the parser only
if __name__ == '__main__':
    # temp_file = "./Seven/Main_temp.xml"
    # out_file = "./Seven/Main.vm"

    # temp_file = "./ConvertToBin/Main_temp.xml"
    # out_file = "./ConvertToBin/Main.vm"

    # temp_file = "./Square/Main_temp.xml"
    # out_file = "./Square/Main.vm"
    # temp_file = "./Square/Square_temp.xml"
    # out_file = "./Square/Square.vm"
    # temp_file = "./Square/SquareGame_temp.xml"
    # out_file = "./Square/SquareGame.vm"

    # temp_file = "./Average/Main_temp.xml"
    # out_file = "./Average/Main.vm"

    # temp_file = "./Pong/Main_temp.xml"
    # out_file = "./Pong/Main.vm"
    # temp_file = "./Pong/Ball_temp.xml"
    # out_file = "./Pong/Ball.vm"
    # temp_file = "./Pong/Bat_temp.xml"
    # out_file = "./Pong/Bat.vm"
    # temp_file = "./Pong/PongGame_temp.xml"
    # out_file = "./Pong/PongGame.vm"

    temp_file = "./ComplexArrays/Main_temp.xml"
    out_file = "./ComplexArrays/Main.vm"

    print(f"Temp XML file: {temp_file}")
    print(f"Output VM file: {out_file}")
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
            line = re.sub("^<[^<>]+>[ ]?", "", line)
            # Remove end tag
            line = re.sub("[ ]?<[^<>]+>\n$", "", line)
            # Remove empty lines
            if line != "\n" and line != "":
                lines.append(line)
                assert tag in {"keyword", "identifier", "symbol", "stringConstant", "integerConstant"}
                tags.append(tag)

    # Initialization of global variables
    class_symbol_table = SymbolTable()
    subroutine_symbol_table = SymbolTable()
    class_var_kind = ""  # field/static variable
    class_var_type = ""  # int, char, boolean or user-defined type
    class_var_name = ""
    class_name = ""  # Used for function naming in vm code (i.e. class_name.function_name)
    subroutine_name = ""
    subroutine_kind = ""  # constructor, function or method
    subroutine_type = ""  # void, int, char, boolean or user-defined type
    label_counter = 0  # Used for handling flow of control (i.e. if/while)

    pos = -1
    with open(out_file, "a") as out_file:
        class_handler(lines, tags, pos, out_file)
