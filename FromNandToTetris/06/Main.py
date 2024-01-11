"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.
    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Initialize the symbol table with all the predefined symbols and their
    # pre-allocated RAM addresses, according to section 6.2.3 of the book.
    my_symbol_table = SymbolTable()
    parser = Parser(input_file)
    first_run(parser, my_symbol_table)
    input_file.seek(0)
    second_run(my_symbol_table, output_file)


def first_run(parser, st):
    """
    Go through the entire assembly program, line by line, and build the symbol
    table without generating any code. As you march through the program lines,
    keep a running number recording the ROM address into which the current
    command will be eventually loaded.
    This number starts at 0 and is incremented by 1 whenever a C-instruction
    or an A-instruction is encountered, but does not change when a label
    pseudo-command or a comment is encountered. Each time a pseudo-command
    (Xxx) is encountered, add a new entry to the symbol table, associating
    Xxx with the ROM address that will eventually store the next command in
    the program.
    This pass results in entering all the program’s labels along with their
    ROM addresses into the symbol table.
    The program’s variables are handled in the second pass.
    """
    while parser.has_more_commands():
        parser.advance()
        eval_commandL(parser, st)


def second_run(st, output_file):
    """
    Now go again through the entire program, and parse each line.
    Each time a symbolic A-instruction is encountered, namely, @Xxx where Xxx
    is a symbol and not a number, look up Xxx in the symbol table.
    If the symbol is found in the table, replace it with its numeric meaning
    and complete the command’s translation.
    If the symbol is not found in the table, then it must represent a new
    variable. To handle it, add the pair (Xxx,n) to the symbol table, where n
    is the next available RAM address, and complete the command’s translation.
    The allocated RAM addresses are consecutive numbers, starting at address
    16 (just after the addresses allocated to the predefined symbols).
    After the command is translated, write the translation to the output file.
    """
    parser = Parser(input_file)
    while parser.has_more_commands():
        parser.advance()
        eval_commandAC(parser, st, output_file)


def eval_commandL(parser, st):
    """
    this function add labels (xxx)  to symbol table ( Xxx :ROM address )
    """
    if parser.command_type() == 'L_COMMAND':
        if not (st.contains(parser.symbol())):
            st.add_entry(parser.symbol(), parser.current_command_line_num)


def eval_commandAC(parser, st, out_file):
    """
    this function handles the translation of A commands and C commands.
    """
    if parser.command_type() == 'A_COMMAND':
        if not (parser.symbol()).isnumeric():
            if not (st.contains(parser.symbol())):
                st.add_entry(parser.symbol(), st.get_n())
                st.advance_n()
            symbol_address = st.get_address(parser.symbol())
            bin_num = bin(symbol_address)
        else:
            bin_num = bin(int(parser.symbol()))
        bin_num = "".join(["0"] * (16 - len(bin_num[2:]))) + bin_num[2:] + '\n'
        out_file.write(bin_num)
    if parser.command_type() == 'C_COMMAND':
        pre_fix = '101' if ('<<' in parser.comp() or '>>' in parser.comp()) else '111'
        bin_com = pre_fix + Code().comp(parser.comp()) + Code().dest(parser.dest()) + Code().jump(parser.jump()) + '\n'
        out_file.write(bin_com)


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
