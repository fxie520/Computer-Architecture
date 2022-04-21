import re
import argparse
import glob
import os

# D = SP--, D = *SP
# noinspection DuplicatedCode
mv_stack_top_to_D = "@SP\n" + \
                    "AM=M-1\n" + \
                    "D=M\n"

# *SP = D, SP++
push_D_to_stack_top = "@SP\n" + \
                      "M=M+1\n" + \
                      "A=M-1\n" + \
                      "M=D\n"

push_A_to_stack_top = "D=A\n" + push_D_to_stack_top

# A = *SP - 1
point_to_2nd_to_last = "@SP\n" + \
                       "A=M-1\n"

# *R13 = D
load_D_to_pointer_R13 = "@R13\n" + \
                        "A=M\n" + \
                        "M=D\n"

base_address_pointers = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
}

# Command types
arithmetic_logical_cmds = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}
memory_segment_cmds = {"push", "pop"}
branching_cmds = {"label", "goto", "if-goto"}
function_cmds = {"function", "call", "return"}


# If D [operation] 0, then M=true, else M=false
# noinspection PyPep8Naming
def compare_D_to_0(operation: str, lbl_counter: int) -> str:
    assert operation in {"JEQ", "JGT", "JLT"}, "Operation name error"
    return "@TRUE" + str(lbl_counter) + "\n" + \
           f"D;{operation}\n" + \
           point_to_2nd_to_last + \
           "M=0\n" + \
           "@CONTINUE" + str(lbl_counter) + "\n" + \
           "0;JMP\n" + \
           "(TRUE" + str(lbl_counter) + ")\n" + \
           point_to_2nd_to_last + \
           "M=-1\n" + \
           "(CONTINUE" + str(lbl_counter) + ")\n"


# noinspection PyPep8Naming,DuplicatedCode
def load_var_to_D(memory_segment: str, var_id: str, f_name: str) -> str:
    assert memory_segment in {"constant", "local", "argument", "this", "that", "temp", "static", "pointer"}, \
        "Operation name error"

    # "@" + var_id + "\n" means @i
    if memory_segment == "constant":
        return "@" + var_id + "\n" + \
               "D=A\n"
    elif memory_segment in {"local", "argument", "this", "that"}:
        return "@" + base_address_pointers[memory_segment] + "\n" + \
               "D=M\n" + \
               "@" + var_id + "\n" + \
               "A=D+A\n" + \
               "D=M\n"
    elif memory_segment == "temp":
        return "@" + str(int(var_id) + 5) + "\n" + \
               "D=M\n"
    elif memory_segment == "static":
        return "@" + f_name + "." + var_id + "\n" + \
               "D=M\n"
    # memory_segment == "pointer"
    else:
        if var_id == "0":
            return "@THIS\n" + \
                   "D=M\n"
        elif var_id == "1":
            return "@THAT\n" + \
                   "D=M\n"
        else:
            raise Exception("Pointer can only be 0 or 1 !")


# R13 = base_address (LCL for ex.) + i
# noinspection PyPep8Naming
def load_var_to_R13(memory_segment: str, var_id: str) -> str:
    assert memory_segment in {"local", "argument", "this", "that"}, "Operation name error"
    return "@" + var_id + "\n" + \
           "D=A\n" + \
           "@" + base_address_pointers[memory_segment] + "\n" + \
           "D=D+M\n" + \
           "@R13\n" + \
           "M=D\n"


# Syntax: push mem_segment i
def push(mem_segment: str, i: str, vm_filename: str) -> str:
    return load_var_to_D(mem_segment, i, vm_filename) + push_D_to_stack_top


# Syntax: pop mem_segment i
def pop(mem_segment: str, i: str, vm_filename: str) -> str:
    if mem_segment in {"local", "argument", "this", "that"}:
        return load_var_to_R13(mem_segment, i) + mv_stack_top_to_D + load_D_to_pointer_R13
    elif mem_segment == "temp":
        return mv_stack_top_to_D + \
               f"@{str(int(i) + 5)}\n" + \
               "M=D\n"
    elif mem_segment == "static":
        return mv_stack_top_to_D + \
               f"@{vm_filename}.{i}\n" + \
               "M=D\n"
    elif mem_segment == "pointer":
        if i == "0":
            return mv_stack_top_to_D + \
                   "@THIS\n" + \
                   "M=D\n"
        elif i == "1":
            return mv_stack_top_to_D + \
                   "@THAT\n" + \
                   "M=D\n"
        else:
            raise Exception("Pointer can only be 0 or 1 !")
    else:  # Memory segment is "constant", which should be an error
        raise Exception("No pop constant operation !")


# Syntax: goto label
def goto(label: str) -> str:
    return f"@{label}\n" + \
           "0;JMP\n"


# Syntax: call function_name nb_args
def call(f_name: str, n_args: str, counter: int = 0) -> str:
    # push return address
    line_to_return = f"@{f_name}.returnAddress{counter}\n".upper() + \
                     push_A_to_stack_top
    # push LCL
    line_to_return = line_to_return + \
        "@LCL\n" + \
        "D=M\n" + \
        push_D_to_stack_top
    # push ARG
    line_to_return = line_to_return + \
        "@ARG\n" + \
        "D=M\n" + \
        push_D_to_stack_top
    # push THIS
    line_to_return = line_to_return + \
        "@THIS\n" + \
        "D=M\n" + \
        push_D_to_stack_top
    # push THAT
    line_to_return = line_to_return + \
        "@THAT\n" + \
        "D=M\n" + \
        push_D_to_stack_top
    # ARG = SP - 5 - nb_args
    line_to_return = line_to_return + \
        "@SP\n" + \
        "D=M\n" + \
        "@5\n" + \
        "D=D-A\n" + \
        f"@{int(n_args)}\n" + \
        "D=D-A\n" + \
        "@ARG\n" + \
        "M=D\n"
    # LCL = SP
    line_to_return = line_to_return + \
        "@SP\n" + \
        "D=M\n" + \
        "@LCL\n" + \
        "M=D\n"
    # goto function_name
    line_to_return = line_to_return + goto(label=f_name)
    # (return address)
    line_to_return = line_to_return + \
        f"({f_name}.returnAddress{counter})\n".upper()
    return line_to_return


# Bootstrap code
def bootstrap() -> str:
    return "// Bootstrap code\n" + \
        "@256\n" + \
        "D=A\n" + \
        "@SP\n" + \
        "M=D\n" + \
        call("Sys.init", "0") + "\n"


if __name__ == '__main__':
    # Parse positional argument
    parser = argparse.ArgumentParser()
    parser.add_argument("input", default=None, type=str,
                        help="Path to a .vm file or a directory containing at least one .vm files")
    args = parser.parse_args()
    print(f"Input: {args.input}")

    # Check input type (single .vm file or a directory containing >=1 .vm files) then extract input & output files
    match = re.search(r"[^/]+\.vm$", args.input)
    # Input is a .vm file
    if match:
        vm_file_name = args.input[match.span()[0]:match.span()[1]].replace(".vm", "")
        vm_file_names = [vm_file_name]
        vm_file_paths = [args.input]
        output_file_path = args.input.replace(".vm", ".asm")
        # Clear output file content
        with open(output_file_path, "w") as output_file:
            pass
    # Input is a directory containing at least one .vm files
    else:
        cwd = os.getcwd()
        os.chdir(args.input)
        vm_file_names = glob.glob("*.vm")
        # Go back to previous directory
        os.chdir(cwd)
        # Remove potential "/" character following the input directory
        input_dir = re.sub("/$", "", args.input)
        vm_file_paths = [input_dir + "/" + vm_file_name for vm_file_name in vm_file_names]
        vm_file_names = [vm_file_name.replace(".vm", "") for vm_file_name in vm_file_names]
        match = re.search(r"[^/]+?$", input_dir)
        if args.input[match.span()[0]:match.span()[1]].startswith("/"):
            output_file_path = input_dir + args.input[match.span()[0]:match.span()[1]] + ".asm"
        else:
            output_file_path = input_dir + "/" + args.input[match.span()[0]:match.span()[1]] + ".asm"
        # Write bootstrap code
        with open(output_file_path, "w") as output_file:
            output_file.write(bootstrap())
            pass

    # Check input contains at least 1 .vm file
    if not vm_file_names:
        raise Exception("No .vm files to process")
    else:
        print(f"Processing .vm files {vm_file_names} with paths {vm_file_paths}")
        print(f"Output file path: {output_file_path}")

    # Label counter, used in assembly commands like "@CONTINUE5" to avoid label repetition.
    label_counter = 0
    # Call counter, used in assembly commands like "@MAIN.FIBONACCI.RETURNADDRESS" to avoid label repetition.
    call_counter = 0

    # Create output file is not exist, else append to it
    with open(output_file_path, "a+") as output_file:
        for vm_file_id, vm_file_path in enumerate(vm_file_paths):
            vm_file_name = vm_file_names[vm_file_id]
            with open(vm_file_path, "r") as f:
                for line_nb, line in enumerate(f):
                    # Ignore comments and blank lines
                    line = re.sub('//.*$', '', line.strip())
                    if not line:
                        continue

                    # Write vm command as a comment in the .asm file for easy debugging
                    output_file.write("// " + line + "\n")

                    # Arithmetic/logical commands
                    # Syntax: add/sub/and/or/neg/not/eq/gt/lt
                    line = line.split()
                    if line[0] in arithmetic_logical_cmds:
                        if line[0] == "add":
                            line_to_write = mv_stack_top_to_D + point_to_2nd_to_last + "M=D+M\n"
                        elif line[0] == "sub":
                            line_to_write = mv_stack_top_to_D + point_to_2nd_to_last + "M=M-D\n"
                        elif line[0] == "and":
                            line_to_write = mv_stack_top_to_D + point_to_2nd_to_last + "M=D&M\n"
                        elif line[0] == "or":
                            line_to_write = mv_stack_top_to_D + point_to_2nd_to_last + "M=D|M\n"
                        elif line[0] == "neg":
                            line_to_write = point_to_2nd_to_last + "M=-M\n"
                        elif line[0] == "not":
                            line_to_write = point_to_2nd_to_last + "M=!M\n"
                        elif line[0] == "eq":
                            label_counter += 1
                            line_to_write = mv_stack_top_to_D + point_to_2nd_to_last + "D=M-D\n" \
                                + compare_D_to_0("JEQ", label_counter)
                        elif line[0] == "gt":
                            label_counter += 1
                            line_to_write = mv_stack_top_to_D + point_to_2nd_to_last + "D=M-D\n" \
                                + compare_D_to_0("JGT", label_counter)
                        else:  # line[0] == "lt"
                            label_counter += 1
                            line_to_write = mv_stack_top_to_D + point_to_2nd_to_last + "D=M-D\n" \
                                + compare_D_to_0("JLT", label_counter)

                    # Memory segment commands
                    # Syntax: push/pop memory_segment i
                    elif line[0] in memory_segment_cmds:
                        if line[0] == "push":
                            line_to_write = push(line[1], line[2], vm_file_name)
                        else:  # line[0] == "pop"
                            line_to_write = pop(line[1], line[2], vm_file_name)

                    # Branching commands
                    # Syntax: label/goto/if-goto LABEL
                    elif line[0] in branching_cmds:
                        if line[0] == "label":
                            line_to_write = f"({line[1]})\n"
                        elif line[0] == "goto":
                            line_to_write = goto(line[1])
                        else:  # line[0] == "if-goto"
                            line_to_write = mv_stack_top_to_D + \
                                            f"@{line[1]}\n" + \
                                            "D;JNE\n"

                    # Function commands
                    elif line[0] in function_cmds:
                        # syntax: function function_name nb_vars
                        if line[0] == "function":
                            nb_vars = int(line[2])
                            line_to_write = f"({line[1]})\n"
                            # "push constant 0" * nb_var times
                            for _ in range(nb_vars):
                                line_to_write = line_to_write + push("constant", "0", "whatever")
                        # syntax: return
                        elif line[0] == "return":
                            # endFrame = LCL
                            line_to_write = "@LCL\n" + \
                                "D=M\n" + \
                                f"@R14\n" + \
                                "M=D\n"
                            # retAddr = *(endFrame - 5)
                            line_to_write = line_to_write + \
                                "@5\n" + \
                                "A=D-A\n" + \
                                "D=M\n" + \
                                "@R15\n" + \
                                "M=D\n"
                            # *ARG = pop()
                            line_to_write = line_to_write + \
                                mv_stack_top_to_D + \
                                "@ARG\n" + \
                                "A=M\n" + \
                                "M=D\n"
                            # SP = ARG + 1
                            line_to_write = line_to_write + \
                                "@ARG\n" + \
                                "D=M+1\n" + \
                                "@SP\n" + \
                                "M=D\n"
                            # THAT = *(endFrame - 1)
                            line_to_write = line_to_write + \
                                "@R14\n" + \
                                "A=M-1\n" + \
                                "D=M\n" + \
                                "@THAT\n" + \
                                "M=D\n"
                            # THIS = *(endFrame - 2)
                            line_to_write = line_to_write + \
                                "@R14\n" + \
                                "D=M\n" + \
                                "@2\n" + \
                                "A=D-A\n" + \
                                "D=M\n" + \
                                "@THIS\n" + \
                                "M=D\n"
                            # ARG = *(endFrame - 3)
                            line_to_write = line_to_write + \
                                "@R14\n" + \
                                "D=M\n" + \
                                "@3\n" + \
                                "A=D-A\n" + \
                                "D=M\n" + \
                                "@ARG\n" + \
                                "M=D\n"
                            # LCL = *(endFrame - 4)
                            line_to_write = line_to_write + \
                                "@R14\n" + \
                                "D=M\n" + \
                                "@4\n" + \
                                "A=D-A\n" + \
                                "D=M\n" + \
                                "@LCL\n" + \
                                "M=D\n"
                            # goto retAddr
                            line_to_write = line_to_write + \
                                "@R15\n" + \
                                "A=M\n" + \
                                "0;JMP\n"
                        # line[0] == "call"
                        # syntax: call function_name nb_args
                        else:
                            call_counter += 1
                            line_to_write = call(line[1], line[2], call_counter)
                    # Command not recognized
                    else:
                        raise Exception(f"Command not recognized in line number {line_nb} of file {f.name}")

                    output_file.write(line_to_write)
                    output_file.write("\n")  # Newline
