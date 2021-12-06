"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from Parser import Parser
from CodeWriter import CodeWriter

C_ARITHMETIC = "C_ARITHMETIC"
C_PUSH = "C_PUSH"
C_POP = "C_POP"
C_FUNCTION = "C_FUNCTION"
C_CALL = "C_CALL"
LABEL_COMMAND = "C_LABEL"
GOTO_COMMAND = "C_GOTO"
IF_GOTO_COMMAND = "C_IF_GOTO"
FUNCTION_COMMAND = "C_FUNCTION"
RETURN_COMMAND = "C_RETURN"
CALL_COMMAND = "C_CALL"


def translate_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Translates a single file.

    Args:
        input_file (typing.TextIO): the file to translate.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    # Note: you can get the input file's name using:
    # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
    parser = Parser(input_file)
    code_writer = CodeWriter(output_file)

    while parser.has_more_commands():
        if parser.command_type() == C_ARITHMETIC:
            command = parser.arg1()
            code_writer.write_arithmetic(command)
        elif parser.command_type() in [C_PUSH, C_POP]:
            segment = parser.arg1()
            index = parser.arg2()
            code_writer.write_push_pop(parser.command_type(), segment, index)
        elif parser.command_type() in [LABEL_COMMAND, GOTO_COMMAND, IF_GOTO_COMMAND]:
            label_name = parser.arg1()
            code_writer.write_branching_command(parser.command_type(), label_name)
        elif parser.command_type() in [FUNCTION_COMMAND, CALL_COMMAND]:
            func = parser.arg1()
            num_args = parser.arg2()
            code_writer.write_function_command(parser.command_type(), func, num_args)
        elif parser.command_type() == RETURN_COMMAND:
            code_writer.write_return_command()
        parser.advance()

    if parser.command_type() == C_ARITHMETIC:
        command = parser.arg1()
        code_writer.write_arithmetic(command)
    elif parser.command_type() in [C_PUSH, C_POP]:
        segment = parser.arg1()
        index = parser.arg2()
        code_writer.write_push_pop(parser.command_type(), segment, index)
    elif parser.command_type() in [LABEL_COMMAND, GOTO_COMMAND, IF_GOTO_COMMAND]:
        label_name = parser.arg1()
        code_writer.write_branching_command(parser.command_type(), label_name)
    elif parser.command_type() in [FUNCTION_COMMAND, CALL_COMMAND]:
        func = parser.arg1()
        num_args = parser.arg2()
        code_writer.write_function_command(parser.command_type(), func, num_args)
    elif parser.command_type() == RETURN_COMMAND:
        code_writer.write_return_command()


if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    with open(output_path, 'w') as output_file:
        for input_path in files_to_translate:
            split_file = input_path.split('\\')
            if split_file[-1] == "Sys.vm":
                print("aaaaa")
                output_file.write("@256" + "\n" + "D=A" + "\n" + "@SP" + "\n" + "M=D" + "\n")
                call_func = '\n'.join(["@return.0", "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1",  #
                                       "@LCL", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",  # saved LCL
                                       "@ARG", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",  # saves ARG
                                       "@THIS", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",  # saves THIS
                                       "@THAT", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1",  # saves THAT
                                       "@SP", "D=M", "@5", "D=D-A", "@0", "D=D-A", "@ARG", "M=D",  # new arg
                                       "@SP", "D=M", "@LCL", "M=D",  # LCL = SP
                                       f"@func.Sys.main", "0;JMP",  # goto function name
                                       "(return.0)", ""])
                output_file.write(call_func)
                code_writer = CodeWriter(output_file)
                func = "Sys.init"
                num_args = 0
                code_writer.write_function_command(C_CALL, func, num_args)
                continue
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file)
