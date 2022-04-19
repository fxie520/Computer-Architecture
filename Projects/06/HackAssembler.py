import re
import os

if __name__ == '__main__':
    dest_table = {
        "M": "001",
        "D": "010",
        "MD": "011",
        "A": "100",
        "AM": "101",
        "AD": "110",
        "AMD": "111",
    }

    jump_table = {
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111",
    }

    comp_table = {
        "M": "1110000",
        "!M": "1110001",
        "-M": "1110011",
        "M+1": "1110111",
        "M-1": "1110010",
        "D+M": "1000010",
        "D-M": "1010011",
        "M-D": "1000111",
        "D&M": "1000000",
        "D|M": "1010101",

        "A": "0110000",
        "!A": "0110001",
        "-A": "0110011",
        "A+1": "0110111",
        "A-1": "0110010",
        "D+A": "0000010",
        "D-A": "0010011",
        "A-D": "0000111",
        "D&A": "0000000",
        "D|A": "0010101",
        "0": "0101010",
        "1": "0111111",
        "-1": "0111010",
        "D": "0001100",
        "!D": "0001101",
        "-D": "0001111",
        "D+1": "0011111",
        "D-1": "0001110",
    }

    # Contains all built-ins and user defined labels & variables.
    symbol_table = {
        # Build-ins
        "R0": "0",
        "R1": "1",
        "R2": "2",
        "R3": "3",
        "R4": "4",
        "R5": "5",
        "R6": "6",
        "R7": "7",
        "R8": "8",
        "R9": "9",
        "R10": "10",
        "R11": "11",
        "R12": "12",
        "R13": "13",
        "R14": "14",
        "R15": "15",
        "SCREEN": "16384",
        "KBD": "24576",
        "SP": "0",
        "LCL": "1",
        "ARG": "2",
        "THIS": "3",
        "THAT": "4",
    }

    file_name = "Rect"
    assert file_name in ["Add", "Pong", "Max", "Rect"]
    assembly_file = "./" + file_name.lower() + "/" + file_name + ".asm"
    temp_file = "./temp.asm"
    # Create directory if not exists
    os.system("[ -d machine_code_files ] || mkdir machine_code_files")
    output_file = "./machine_code_files/" + file_name + ".hack"

    # First pass: remove all comments, blank lines & indentations
    with open(assembly_file, 'r') as f:
        lines = f.readlines()
    with open(temp_file, 'w') as f:
        for line in lines:
            # Remove all comments & indentations
            line_to_write = re.sub('//.*$', '', line.strip(' '))
            # Remove blank lines
            if line_to_write != '\n':
                f.write(line_to_write)

    # Second pass: add labels to the symbol table
    with open(temp_file, 'r') as f:
        lines = f.readlines()
    line_count = 0
    with open(temp_file, 'w') as f:
        for line in lines:
            match = re.match(r'\(.+\)', line)
            # If label presents
            if match:
                # label without parentheses
                label = line[match.span()[0]+1:match.span()[1]-1]
                symbol_table[label] = str(line_count)
            else:
                f.write(line)
                line_count += 1

    # Third pass: translate the entire program
    with open(temp_file, 'r') as f:
        lines = f.readlines()
    var_pos_in_RAM = 16  # Variable position in RAM
    with open(output_file, 'w') as out_file:
        for line in lines:
            # A-instruction
            if line.startswith('@'):
                value = line.strip()[1:]  # Strip new line character and the "@" symbol
                # If value is non-numeric, i.e. a variable
                if not re.fullmatch('^[0-9]+$', value):
                    # If variable already declared
                    if value in symbol_table:
                        value = symbol_table[value]
                    # Declare new variable
                    else:
                        symbol_table[value] = var_pos_in_RAM
                        value = var_pos_in_RAM
                        var_pos_in_RAM += 1
                value = bin(int(value)).replace("0b", "")  # Decimal to binary
                instr = "0"*(16 - len(value)) + value  # Add leading zeros so that the instruction has 16 characters
            # C-instruction
            else:
                line = line.strip()  # Strip new line character
                pos_equal_sign = line.find('=')
                pos_semi_colon = line.find(';')
                # If the equal sign is found, i.e. destination exists
                if pos_equal_sign >= 0:
                    dest = dest_table[line[:pos_equal_sign]]
                else:
                    dest = "000"
                # If the semicolon sign is found, i.e. jump exists
                if pos_semi_colon >= 0:
                    jump = jump_table[line[pos_semi_colon + 1:]]
                    comp = comp_table[line[pos_equal_sign + 1:pos_semi_colon]]
                else:
                    jump = "000"
                    comp = comp_table[line[pos_equal_sign + 1:]]
                instr = "111" + comp + dest + jump
            out_file.write(instr + '\n')

    # Remove the temporary file
    os.system("rm temp.asm")
