from Utils import *
import os
import re
import argparse


def tokenizer(f_path: str):
    assert os.path.exists(f_path), "File path does not exist !"
    f_dir = os.path.dirname(f_path)
    f_name = os.path.basename(f_path).replace(".jack", "")
    f_output = f_dir + f"/{f_name}_temp.xml"
    print(f"Tokenizing input: {f_path}")
    print(f"Tokenizer output: {f_output}")

    # First pass: reformat input file into one line
    f_content = ""
    ignore_line = False  # Whether ignore next line or not
    with open(f_path, 'r') as f:
        for nb, line in enumerate(f):
            if ignore_line:
                # If multi-line comment ends in this line
                if re.search("^.*[*]/", line):
                    ignore_line = False
                    line = re.sub("^.*[*]/", "", line)
                else:
                    continue
            # Remove different types of comments
            line = re.sub('//.*$', '', line)
            if re.search("/[*]", line):
                # /*(*) One line comment */
                if re.search(r'/\*.*\*/', line):
                    line = re.sub(r'/\*.*\*/', '', line)
                # /*(*) multiple line
                # comment */
                else:
                    line = re.sub(r'/[*].*$', '', line)
                    ignore_line = True

            # Remove indentations & tabs
            line = line.strip(' 	')
            # Remove empty lines
            line = re.sub("^\n$", '', line)
            # Remove remaining newline characters
            line = line.replace('\n', ' ')
            # Reformat so that each symbol is surrounded with one space at each side
            # Note that <, >, " and & symbols are replaced with &lt; etc. so that the
            # resulting XML file can be rendered correctly in a browser.
            temp = symbols.copy()
            temp.append("\"")
            for symbol in temp:
                if symbol in line:
                    # "\\" is not an error even if it is flagged by PyCharm
                    line = re.sub("[ ]*" + "\\" + symbol + r"[ ]*", " " + symbol + " ", line)
                    line = re.sub("\\" + symbol, symbol.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                                  .replace("\"", "&quot;") + " ", line)
            # Append file content
            f_content = f_content + line
    # Replace each occurrence of multiple spaces by a single space
    f_content = re.sub("[ ]+", " ", f_content.strip(" "))
    # print(f"Input file in one line: \n{f_content}")

    # Start tokenization
    f_content = f_content.split(" ")
    # print(f"Input file split in words: \n{f_content}")
    is_string = False
    with open(f_output, 'w') as f:
        f.write("<tokens>\n")
        for word in f_content:
            if word != "&quot;" and not is_string:
                if word in keywords:
                    f.write("<keyword> " + word + " </keyword>\n")
                elif (word in symbols) or (word in xml_symbols):
                    f.write("<symbol> " + word + " </symbol>\n")
                elif word.isnumeric():
                    assert 0 <= int(word) <= 32767, "Integer constant must be between 0 and 32767 (both end inclusive)"
                    f.write("<integerConstant> " + word + " </integerConstant>\n")
                else:
                    f.write("<identifier> " + word + " </identifier>\n")
            # First double quote of a string
            elif word == "&quot;" and not is_string:
                is_string = True
                string = ""
            # Middle of a string
            elif word != "&quot;" and is_string:
                string = string + word + " "
            # Final double quote of a string
            else:
                is_string = False
                f.write("<stringConstant> " + string + "</stringConstant>\n")
        f.write("</tokens>")
    return


# Driver code for debugging the tokenizer only
if __name__ == '__main__':
    # Parse positional argument
    parser = argparse.ArgumentParser()
    parser.add_argument("input", default=None, type=str,
                        help="Path to a .jack file or a directory containing at least one .jack file")
    args = parser.parse_args()
    # args = parser.parse_args('./Square/Square.jack'.split())
    print(f"Input: {args.input}")

    jack_files = []
    if os.path.isdir(args.input):
        for file in os.listdir(args.input):
            if file.endswith(".jack"):
                jack_files.append(os.path.join(args.input, file))
    elif args.input.endswith(".jack"):
        jack_files.append(args.input)
    else:
        raise Exception("Input must be a .jack file or a directory containing at least one .jack file !")
    print(f"Tokenizing jack files: {jack_files}")

    for jack_file in jack_files:
        tokenizer(jack_file)
