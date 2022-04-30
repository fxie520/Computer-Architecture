import os
import argparse
import re
from Tokenizer import *
from Parser import *


if __name__ == '__main__':
    # Parse positional argument
    parser = argparse.ArgumentParser()
    parser.add_argument("input", default=None, type=str,
                        help="Path to a .jack file or a directory containing at least one .jack file")
    args = parser.parse_args()
    print(f"Input: {args.input}")

    # Extract jack files to process
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

    # Generate tokenized files (aka temp files) and extract final xml files (aka out_files)
    temp_files = []
    out_files = []
    for jack_file in jack_files:
        temp_file = jack_file.replace(".jack", "_temp.xml")
        temp_files.append(temp_file)
        out_file = jack_file.replace(".jack", ".vm")
        out_files.append(out_file)
        tokenizer(jack_file)

    # Parse each tokenized file
    for i, temp_file in enumerate(temp_files):
        # Clear output file
        out_file = out_files[i]
        with open(out_file, "w") as _:
            pass

        # Read tokenized file and extract xml tags & contents into the 2 following lists
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

        # Remove temp file
        os.system(f"rm {temp_file}")

        # Parse file
        pos = -1
        with open(out_file, "a") as out_file:
            class_handler(lines, tags, pos, out_file)
