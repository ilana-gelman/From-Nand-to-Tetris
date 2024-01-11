"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from CompilationEngine import CompilationEngine
from JackTokenizer import JackTokenizer
# from SymbolTable import SymbolTable

comp_dict = {'<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;'}


def eat(out, lexical_element, val):
    out.write(f"<{lexical_element}> " + str(val) + f" </{lexical_element}>\n")


def analyze_file(input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Analyzes a single file.

    Args:
        input_file (typing.TextIO): the file to analyze.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    # st = SymbolTable
    parser = JackTokenizer(input_file)
    token_file = open('token_file.xml', 'w')
    create_token_file(parser, token_file)
    token_file.close()
    token_file = open('token_file.xml', 'r')
    compiler = CompilationEngine(token_file, output_file)
    compiler.compile_class()


def create_token_file(parser, token_file):
    token_file.write("<tokens>\n")
    while parser.has_more_tokens():
        parser.advance()
        if parser.token_type() == "STRING_CONST":
            eat(token_file, "stringConstant", parser.string_val())
        if parser.token_type() == "KEYWORD":
            eat(token_file, "keyword", parser.keyword().lower())
        if parser.token_type() == "SYMBOL":
            sy = parser.symbol()
            if sy in comp_dict:
                sy = comp_dict[sy]
            eat(token_file, "symbol", sy)

        if parser.token_type() == "IDENTIFIER":
            eat(token_file, "identifier", parser.identifier())

        if parser.token_type() == "INT_CONST":
            eat(token_file, "integerConstant", parser.int_val())
    token_file.write("</tokens>\n")


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: JackAnalyzer <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".jack":
            continue
        output_path = filename + ".xml"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            analyze_file(input_file, output_file)
