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
    var_kind, var_type = list(var_dec_root)[:2]
    for var_name in list(var_dec_root)[2:-1:2]:
        symbol_table.define(var_name.text.strip(), var_type.text.strip(), var_kind.text.strip())


def compile_subroutine(subroutine_root: Element, symbol_table: SymbolTable, writer: VMWriter):
    symbol_table.start_subroutine()

    func_name = list(subroutine_root)[2].text.strip()
    num_args = 1 if list(subroutine_root)[0].text.strip() == "method" else 0
    num_args += store_parameter_list(list(subroutine_root)[4], symbol_table)
    writer.write_function(func_name, num_args)

    return_type = list(subroutine_root)[1].text.strip()
    if return_type == writer.class_name:
        object_size = symbol_table.var_count("field")
        writer.write_push("constant", object_size)
        writer.write_call("Memory.alloc", 1)
        writer.write_pop("pointer", 0)

    body = list(subroutine_root)[6]
    for block in list(body)[1:-1]:
        if block.tag == "varDec":
            store_var_dec(block, symbol_table)
        elif block.tag == "statements":
            compile_statements(block, symbol_table, writer)


def store_parameter_list(var_dec_root: Element, symbol_table: SymbolTable) -> int:
    for i in range(len(var_dec_root))[::3]:
        symbol_table.define(list(var_dec_root)[i+1].text.strip(), list(var_dec_root)[i].text.strip(), "argument")
    return int((len(list(var_dec_root)) + 1) / 3)


def compile_statements(statements_root: Element, symbol_table: SymbolTable, writer: VMWriter):
    for statement in statements_root:
        if statement.tag.text == "doStatement":
            compile_do(statement, symbol_table, writer)
        elif statement.tag.text == "ifStatement":
            compile_if(statement, symbol_table, writer)
        elif statement.tag.text == "whileStatement":
            compile_while(statement, symbol_table, writer)
        elif statement.tag.text == "letStatement":
            compile_let(statement, symbol_table, writer)
        elif statement.tag.text == "returnStatement":
            compile_return(statement, symbol_table, writer)


def compile_do():
    pass


def compile_let():
    pass


def compile_while():
    pass


def compile_return():
    pass


def compile_if():
    pass


def compile_expression():
    pass


def compile_term():
    pass


def compile_expression_list():
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
