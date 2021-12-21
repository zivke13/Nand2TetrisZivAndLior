"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from xml.etree.ElementTree import Element
from CompilationEngine import CompilationEngine
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter


def store_var_dec(var_dec_root: Element, symbol_table: SymbolTable):
    var_kind, var_type, var_name, _ = list(var_dec_root)
    symbol_table.define(var_name.text.strip(), var_type.text.strip(), var_kind.text.strip())


def compile_subroutine(subroutine_root: Element, symbol_table: SymbolTable, writer: VMWriter):
    pass


def compile_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Compiles a single file.

    Args:
        input_file (typing.TextIO): the file to compile.
        output_file (typing.TextIO): writes all output to this file.
    """
    tokenizer = JackTokenizer(input_file)
    engine = CompilationEngine(input_file, output_file, tokenizer)
    engine.compile_class()

    root = engine.root
    top_level_tags: typing.List[Element] = list(root)
    class_name = top_level_tags[1].text.strip()

    writer = VMWriter(output_file, class_name)
    symbol_table = SymbolTable()

    for dec in top_level_tags[3:-1]:
        if dec.tag == "classVarDec":
            store_var_dec(dec, symbol_table)

        elif dec.tag == "subroutineDec":
            compile_subroutine(dec, symbol_table, writer)

    writer.close()


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: JackCompiler <input path>")
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
        output_path = filename + ".vm"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            compile_file(input_file, output_file)
