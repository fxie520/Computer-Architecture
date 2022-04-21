import re
import argparse


# If D [operation] 0, then M=true, else M=false
# noinspection PyPep8Naming,DuplicatedCode
def compare_D_to_0(operation: str) -> str:
    assert operation in {"JEQ", "JGT", "JLT"}, "Operation name error"
    return "@TRUE" + str(label_counter) + "\n" + \
           f"D;{operation}\n" + \
           point_to_2nd_to_last + \
           "M=0\n" + \
           "@CONTINUE" + str(label_counter) + "\n" + \
           "0;JMP\n" + \
           "(TRUE" + str(label_counter) + ")\n" + \
           point_to_2nd_to_last + \
           "M=-1\n" + \
           "(CONTINUE" + str(label_counter) + ")\n"


# D = SP--, D = *SP
# noinspection DuplicatedCode
mv_stack_top_to_D = "@SP\n" + \
                    "AM=M-1\n" + \
                    "D=M\n"
# *SP = D, SP++
load_D_to_stack_top = "@SP\n" + \
                      "M=M+1\n" + \
                      "A=M-1\n" + \
                      "M=D\n"
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # Positional argument
    parser.add_argument("input_vm_file", default=None, type=str, help="Path to *.vm file")
    args = parser.parse_args()

    # Get file name, i.e. *.vm without path
    match = re.search(r"[^/]+\.vm$", args.input_vm_file)
    file_name = args.input_vm_file[match.span()[0]:match.span()[1]]

    # Command types
    # noinspection DuplicatedCode
    arithmetic_logical_cmds = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}
    memory_segment_cmds = {"push", "pop"}

    # Branching label counter
    label_counter = 0

    with open(args.input_vm_file, "r") as f:
        output_file = args.input_vm_file.replace(".vm", ".asm")
        with open(output_file, "w") as output:
            for line_nb, line in enumerate(f):
                # Ignore comments and blank lines
                line = re.sub('//.*$', '', line.strip())
                if not line:
                    continue

                # For debugging
                output.write("// " + line + "\n")

                # Arithmetic/logical commands
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
                        line_to_write = mv_stack_top_to_D + point_to_2nd_to_last + "D=M-D\n" + compare_D_to_0("JEQ")
                    elif line[0] == "gt":
                        label_counter += 1
                        line_to_write = mv_stack_top_to_D + point_to_2nd_to_last + "D=M-D\n" + compare_D_to_0("JGT")
                    # line[0] == "lt":
                    else:
                        label_counter += 1
                        line_to_write = mv_stack_top_to_D + point_to_2nd_to_last + "D=M-D\n" + compare_D_to_0("JLT")
                # Memory segment commands
                elif line[0] in memory_segment_cmds:
                    if line[0] == "push":
                        line_to_write = load_var_to_D(line[1], line[2], file_name) + load_D_to_stack_top
                    # line[0] == "pop"
                    else:
                        if line[1] in {"local", "argument", "this", "that"}:
                            line_to_write = load_var_to_R13(line[1], line[2]) + mv_stack_top_to_D + \
                                            load_D_to_pointer_R13
                        elif line[1] == "temp":
                            line_to_write = mv_stack_top_to_D + \
                                            "@" + str(int(line[2]) + 5) + "\n" + \
                                            "M=D\n"
                        elif line[1] == "static":
                            line_to_write = mv_stack_top_to_D + \
                                            "@" + file_name + "." + line[2] + "\n" + \
                                            "M=D\n"
                        elif line[1] == "pointer":
                            if line[2] == "0":
                                line_to_write = mv_stack_top_to_D + \
                                                "@THIS\n" + \
                                                "M=D\n"
                            elif line[2] == "1":
                                line_to_write = mv_stack_top_to_D + \
                                                "@THAT\n" + \
                                                "M=D\n"
                            else:
                                raise Exception("Pointer can only be 0 or 1 !")
                        # Memory segment is "constant"
                        else:
                            raise Exception("No pop constant operation !")
                # Command not recognized
                else:
                    raise Exception(f"Command not recognized in line number {line_nb} of file {f.name}")

                output.write(line_to_write)
                output.write("\n")  # Newline
