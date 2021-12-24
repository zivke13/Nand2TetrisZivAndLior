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

OPS = {
    "+": "add",
    "-": "sub",
    "<": "lt",
    ">": "gt",
    "&": "and",
    "|": "or",
    "=": "eq"
}
label_counter = 0


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
    if return_type == writer.class_name:  # TODO: other classes size
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


def compile_while(while_root: Element, symbol_table: SymbolTable, writer: VMWriter):
    global label_counter
    first_label = f"label.{label_counter}"
    label_counter += 1
    second_label = f"label.{label_counter}"
    label_counter += 1

    writer.write_label(first_label)
    compile_expression(list(while_root)[2], symbol_table, writer)
    writer.write_arithmetic("not")

    writer.write_if(second_label)
    compile_statements(list(while_root)[5], symbol_table, writer)

    writer.write_goto(first_label)
    writer.write_label(second_label)


def compile_return(return_root: Element, symbol_table: SymbolTable, writer: VMWriter):
    if list(return_root)[1].tag == "expression":
        compile_expression(list(return_root)[1], symbol_table, writer)
    else:
        writer.write_push("constant", 0)
    writer.write_return()


def compile_if(if_root: Element, symbol_table: SymbolTable, writer: VMWriter):
    global label_counter
    first_label = f"label.{label_counter}"
    label_counter += 1
    second_label = f"label.{label_counter}"
    label_counter += 1

    compile_expression(list(if_root)[2], symbol_table, writer)
    writer.write_arithmetic("not")

    writer.write_if(first_label)
    compile_statements(list(if_root)[5], symbol_table, writer)
    writer.write_goto(second_label)
    writer.write_label(first_label)
    if len(list(if_root)) > 7 and list(if_root)[7].text.strip() == "else":
        compile_statements(list(if_root)[9], symbol_table, writer)
    writer.write_label(second_label)


def compile_expression(expression_root: Element, symbol_table: SymbolTable, writer: VMWriter):
    compile_term(list(expression_root)[0], symbol_table, writer)

    expression_count = len(list(expression_root))
    for i in range(2, expression_count, 2):
        compile_term(list(expression_root)[i], symbol_table, writer)
        compile_op(list(expression_root)[i-1], symbol_table, writer)


def compile_op(op_root: Element, symbol_table: SymbolTable, writer: VMWriter):
    writer.write_arithmetic(OPS[op_root.text.strip()])  # TODO: mul and div


def compile_term(term_root: Element, symbol_table: SymbolTable, writer: VMWriter):
    if len(term_root) == 1:
        compile_length_1_term(term_root, symbol_table, writer)

    elif len(term_root) == 2 and list(term_root)[0].tag == "symbol":
        compile_term(list(term_root)[1], symbol_table, writer)
        op = list(term_root)[0].text.strip()
        writer.write_arithmetic("neg" if op == "-" else "not")

    elif is_function_call(term_root):
        compile_function_call_term(term_root, symbol_table, writer)

    elif is_parentheses_exp(term_root):
        compile_expression(list(term_root)[1], symbol_table, writer)


def compile_function_call_term(term_root: Element, symbol_table: SymbolTable, writer: VMWriter):
    func_name = list(term_root)[:-3]
    exp_list = list(term_root)[-2]
    if len(func_name) == 1:
        writer.write_push("pointer", 0)
        compile_expression_list(exp_list, symbol_table, writer)
        writer.write_call(func_name[0].text.strip(), len(exp_list) + 1)
    elif len(func_name) == 3:
        caller = func_name[0].text.strip()
        name = func_name[2].text.strip()
        segment = symbol_table.kind_of(caller)
        if segment is None:
            compile_expression_list(exp_list, symbol_table, writer)
            writer.write_call(f"{caller}.{name}", len(exp_list))
        else:
            if segment == "field":
                segment = "this"
            elif segment == "var":
                segment = "local"
            idx = symbol_table.index_of(caller)
            writer.write_push(segment, idx)
            compile_expression_list(exp_list, symbol_table, writer)
            func_class = symbol_table.type_of(caller)
            writer.write_call(f"{func_class}.{name}", len(exp_list) + 1)


def compile_length_1_term(term_root: Element, symbol_table: SymbolTable, writer: VMWriter):
    tag = list(term_root)[0]
    if tag.tag == "keyword":
        compile_keyword(tag.text.strip(), writer)
    elif tag.tag == "integerConstant":
        writer.write_push("constant", tag.text.strip())
    elif tag.tag == "stringInteger":
        compile_string(tag.text.strip(), writer)
    elif tag.tag == "identifier":
        segment = symbol_table.kind_of(tag.text.strip())
        if segment == "field":
            segment = "this"
        elif segment == "var":
            segment = "local"
        writer.write_push(segment, symbol_table.index_of(tag.text.strip()))


def compile_keyword(keyword: str, writer: VMWriter):
    if keyword == "false":
        writer.write_push("constant", 0)
    elif keyword == "true":
        writer.write_push("constant", -1)
    elif keyword == "null":
        writer.write_push("constant", 0)
    elif keyword == "this":
        writer.write_push("pointer", 0)


def compile_string(string: str, writer: VMWriter):
    writer.write_push("constant", len(string))
    writer.write_call("String.new", 1)

    for c in string:
        writer.write_push("constant", ord(c))
        writer.write_call("String.appendChar", 1)


def compile_expression_list(exp_list_root: Element, symbol_table: SymbolTable, writer: VMWriter):
    for exp in exp_list_root:
        compile_expression(exp, symbol_table, writer)


def is_function_call(term_root: Element):
    elements = list(term_root)
    return elements[-3].text.strip() == "(" and elements[-2].tag == "expressionList" and \
           elements[-1].text.strip() == ")"


def is_parentheses_exp(term_root: Element):
    elements = list(term_root)
    return len(elements) == 3 and elements[0].text.strip() == "(" and elements[1].tag == "expression" and \
           elements[2].text.strip() == ")"


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
