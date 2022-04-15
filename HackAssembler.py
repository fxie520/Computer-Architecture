import re

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

    assembly_file = "./add/Add.asm"

    # First pass: remove all comments, blank lines & indentations
    with open(assembly_file, 'r') as f:
        lines = f.readlines()
    with open(assembly_file, 'w') as f:
        for line in lines:
            # Remove all comments & indentations
            line_to_write = re.sub('//.*$', '', line.strip(' '))
            # Remove blank lines
            if line_to_write != '\n':
                f.write(line_to_write)
