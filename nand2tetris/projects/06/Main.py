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


A_COMMAND = "A_COMMAND"
C_COMMAND = "C_COMMAND"
L_COMMAND = "L_COMMAND"


def int_to_16_bit_binary(num: int) -> str:
    return "{0:b}".format(num).zfill(16)


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    parser = Parser(input_file)
    symbol_table = SymbolTable()
    code = Code()

    variable_count = 16
    output_lines = []

    while parser.has_more_commands():
        if parser.command_type() == L_COMMAND:
            symbol = parser.symbol()
            line_number = parser.line_number
            symbol_table.add_entry(symbol, line_number)
            parser.remove_line()
        else:
            parser.advance()
    parser.restart()

    while parser.has_more_commands():
        if parser.command_type() == A_COMMAND:
            symbol = parser.symbol()
            if symbol.isdigit():
                parser.advance()
                continue
            if not symbol_table.contains(symbol):
                symbol_table.add_entry(symbol, variable_count)
                variable_count += 1
        parser.advance()
    parser.restart()

    while parser.has_more_commands():
        if parser.command_type() == A_COMMAND:
            symbol = parser.symbol()
            if not symbol.isdigit():
                symbol = symbol_table.get_address(symbol)
            output_lines.append(int_to_16_bit_binary(int(symbol)))
        elif parser.command_type() == C_COMMAND:
            comp = code.comp(parser.comp())
            dest = code.dest(parser.dest())
            jump = code.jump(parser.jump())
            output_lines.append(f'111{comp}{dest}{jump}')
        parser.advance()
    if parser.command_type() == A_COMMAND:
        symbol = parser.symbol()
        if not symbol.isdigit():
            symbol = symbol_table.get_address(symbol)
        output_lines.append(int_to_16_bit_binary(int(symbol)))
    elif parser.command_type() == C_COMMAND:
        comp = code.comp(parser.comp())
        dest = code.dest(parser.dest())
        jump = code.jump(parser.jump())
        output_lines.append(f'111{comp}{dest}{jump}')

    output_file.write('\n'.join(output_lines))


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
