"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


ADD_COMMAND = "add"
SUB_COMMAND = "sub"
NEG_COMMAND = "neg"
EQ_COMMAND = "eq"
GT_COMMAND = "gt"
LT_COMMAND = "lt"
AND_COMMAND = "and"
OR_COMMAND = "or"
NOT_COMMAND = "not"
SHR_COMMAND = "shiftright"
SHL_COMMAND = "shiftleft"


PUSH_COMMAND = "C_PUSH"
POP_COMMAND = "C_POP"

CONSTANT_SEGMENT = "constant"

LOCAL_SEGMENT = "local"
ARG_SEGMENT = "argument"
THIS_SEGMENT = "this"
THAT_SEGMENT = "that"

STATIC_SEGMENT = "static"
TEMP_SEGMENT = "temp"
POINTER_SEGMENT = "pointer"

SEGMENT_TO_NAME = {
    LOCAL_SEGMENT: "LCL",
    ARG_SEGMENT: "ARG",
    THIS_SEGMENT: "THIS",
    THAT_SEGMENT: "THAT"
}

POINTER_VALUE = {
    0: "THIS",
    1: 'THAT'
}


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output = output_stream
        self.filename = ""
        self.custom_label_count = 0

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.filename = filename
        self.output.write(f'// {filename}\n')

    @staticmethod
    def _translate_add() -> str:
        return '\n'.join(["@SP", "A=M-1", "D=M", "A=A-1", "M=D+M", "@SP", "M=M-1"]) + '\n'

    @staticmethod
    def _translate_sub() -> str:
        return '\n'.join(["@SP", "A=M-1", "D=-M", "A=A-1", "M=D+M", "@SP", "M=M-1"]) + '\n'

    @staticmethod
    def _translate_neg() -> str:
        return '\n'.join(["@SP", "A=M-1", "M=-M"]) + '\n'

    def _translate_eq(self) -> str:
        self.custom_label_count += 1
        return '\n'.join(["@SP", "A=M-1", "D=M", "A=A-1", "D=D-M",  # calc the sub of the last two numbers
                          f"@true.gt.{self.custom_label_count}", "D;JEQ",  # jump to store false if needed
                          "@SP", "A=M-1", "A=A-1", "M=0", f"@false.gt.{self.custom_label_count}", "0;JMP",  # store false
                          f"(true.gt.{self.custom_label_count})", "@SP", "A=M-1", "A=A-1", "M=-1",  # store true
                          f"(false.gt.{self.custom_label_count})", "@SP", "M=M-1"]) + '\n'  # end and change SP

    def _translate_gt(self) -> str:
        self.custom_label_count += 1
        return '\n'.join(["@SP", "A=M-1", "D=M", "A=A-1", "D=D-M",  # calc the sub of the last two numbers
                          f"@false.gt.{self.custom_label_count}", "D;JGE",  # jump to store false if needed
                          "@SP", "A=M-1", "A=A-1", "M=-1", f"@true.gt.{self.custom_label_count}", "0;JMP",  # store true
                          f"(false.gt.{self.custom_label_count})", "@SP", "A=M-1", "A=A-1", "M=0",  # store false
                          f"(true.gt.{self.custom_label_count})", "@SP", "M=M-1"]) + '\n'  # end and change SP

    def _translate_lt(self) -> str:
        self.custom_label_count += 1
        return '\n'.join(["@SP", "A=M-1", "D=M", "A=A-1", "D=D-M",  # calc the sub of the last two numbers
                          f"@false.gt.{self.custom_label_count}", "D;JLE",  # jump to store false if needed
                          "@SP", "A=M-1", "A=A-1", "M=-1", f"@true.gt.{self.custom_label_count}", "0;JMP",  # store true
                          f"(false.gt.{self.custom_label_count})", "@SP", "A=M-1", "A=A-1", "M=0",  # store false
                          f"(true.gt.{self.custom_label_count})", "@SP", "M=M-1"]) + '\n'  # end and change SP

    @staticmethod
    def _translate_and() -> str:
        return '\n'.join(["@SP", "A=M-1", "D=M", "A=A-1", "M=D&M", "@SP", "M=M-1"]) + '\n'

    @staticmethod
    def _translate_or() -> str:
        return '\n'.join(["@SP", "A=M-1", "D=M", "A=A-1", "M=D|M", "@SP", "M=M-1"]) + '\n'

    @staticmethod
    def _translate_not() -> str:
        return '\n'.join(["@SP", "A=M-1", "M=!M"]) + '\n'

    def _translate_shr(self) -> str:
        self.custom_label_count += 1
        return '\n'.join(["@SP", "A=M-1", "D=M", f"@shr.isneg.{self.custom_label_count}", "M=D",  # store M
                          f"@start.pos.{self.custom_label_count}", "D;JGE",  # skip if positive
                          "@SP", "A=M-1", "M=-M",  # neg M
                          f"(start.pos.{self.custom_label_count})",  # start normal flow
                          f"@shr.counter.{self.custom_label_count}", "M=0",  # initialize 0 in the counter
                          f"(shr.loop.{self.custom_label_count})",  # loop's start
                          "@SP", "A=M-1", "D=M",  # store stack's top value in D
                          "D=D-1", f"@shr.end.{self.custom_label_count}", "D;JLE",  # jump to the loop's end if D<2
                          "@SP", "A=M-1", "M=M-1", "M=M-1",  # decrease the stack's top value by 2
                          f"@shr.counter.{self.custom_label_count}", "M=M+1",  # increase the counter by 1
                          f"@shr.loop.{self.custom_label_count}", "0;JMP",  # jump to the loop's start
                          f"(shr.end.{self.custom_label_count})", f"@shr.counter.{self.custom_label_count}",
                          "D=M", "@SP", "A=M-1", "M=D",  # store the counter in the stack
                          f"@shr.isneg.{self.custom_label_count}", "D=M",  # store the initial value in D
                          f"@end.pos.{self.custom_label_count}", "D;JGE",  # jump to end if positive
                          "@SP", "A=M-1", "M=-M",  # neg SP
                          f"(end.pos.{self.custom_label_count})"]) + '\n'  # end

    @staticmethod
    def _translate_shl() -> str:
        return '\n'.join(["@SP", "A=M-1", "D=M", "M=D+M"]) + '\n'

    @staticmethod
    def _translate_push_const(index: int) -> str:
        return '\n'.join([f"@{index}", "D=A", "@SP", "A=M", "M=D", "@SP", "M=M+1"]) + '\n'

    @staticmethod
    def _translate_pop_const(index: int) -> str:
        return '\n'.join(["@SP", "A=M-1", "D=M", f"@{index}", "M=D", "@SP", "M=M-1"]) + '\n'

    @staticmethod
    def _translate_push_dynamic(segment: str, index: int) -> str:
        return '\n'.join([f"@{index}", "D=A", f"@{SEGMENT_TO_NAME[segment]}", "A=D+M", "D=M",
                          "@SP", "A=M", "M=D", "@SP", "M=M+1"]) + '\n'

    @staticmethod
    def _translate_pop_dynamic(segment: str, index: int) -> str:
        return '\n'.join([f"@{SEGMENT_TO_NAME[segment]}", "D=M", f"@{index}", "D=D+A",  # store the right index in D
                          "@SP", "A=M", "M=D", "A=A-1", "D=M", "A=A+1", "A=M", "M=D",  # store the value from the stack
                          "@SP", "M=M-1"]) + '\n'  # decrease the stack pointer

    def _translate_push_static(self, index: int) -> str:
        return '\n'.join([f"@{self.filename}.{index}", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1"]) + '\n'

    def _translate_pop_static(self, index: int) -> str:
        return '\n'.join(["@SP", "A=M-1", "D=M", f"@{self.filename}.{index}", "M=D", "@SP", "M=M-1"]) + '\n'

    @staticmethod
    def _translate_push_temp(index: int) -> str:
        return '\n'.join([f"@R{5 + index}", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1"]) + '\n'

    @staticmethod
    def _translate_pop_temp(index: int) -> str:
        return '\n'.join(["@SP", "A=M-1", "D=M", f"@R{5 + index}", "M=D", "@SP", "M=M-1"]) + '\n'

    @staticmethod
    def _translate_push_pointer(index: int) -> str:
        return '\n'.join([f"@{POINTER_VALUE[index]}", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1"]) + '\n'

    @staticmethod
    def _translate_pop_pointer(index: int) -> str:
        return '\n'.join(["@SP", "A=M-1", "D=M", f"@{POINTER_VALUE[index]}", "M=D", "@SP", "M=M-1"]) + '\n'

    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given 
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        self.output.write(f"// {command}\n")
        if command == ADD_COMMAND:
            self.output.write(self._translate_add())
        elif command == SUB_COMMAND:
            self.output.write(self._translate_sub())
        elif command == SHR_COMMAND:
            self.output.write(self._translate_shr())
        elif command == SHL_COMMAND:
            self.output.write(self._translate_shl())
        elif command == NEG_COMMAND:
            self.output.write(self._translate_neg())
        elif command == EQ_COMMAND:
            self.output.write(self._translate_eq())
        elif command == GT_COMMAND:
            self.output.write(self._translate_gt())
        elif command == LT_COMMAND:
            self.output.write(self._translate_lt())
        elif command == AND_COMMAND:
            self.output.write(self._translate_and())
        elif command == OR_COMMAND:
            self.output.write(self._translate_or())
        elif command == NOT_COMMAND:
            self.output.write(self._translate_not())

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        self.output.write(f"// {command} {segment} {index}\n")
        if segment == CONSTANT_SEGMENT:
            if command == PUSH_COMMAND:
                self.output.write(self._translate_push_const(index))
            if command == POP_COMMAND:
                self.output.write(self._translate_pop_const(index))

        elif segment in [LOCAL_SEGMENT, ARG_SEGMENT, THIS_SEGMENT, THAT_SEGMENT]:
            if command == PUSH_COMMAND:
                self.output.write(self._translate_push_dynamic(segment, index))
            if command == POP_COMMAND:
                self.output.write(self._translate_pop_dynamic(segment, index))

        elif segment == STATIC_SEGMENT:
            if command == PUSH_COMMAND:
                self.output.write(self._translate_push_static(index))
            if command == POP_COMMAND:
                self.output.write(self._translate_pop_static(index))

        elif segment == TEMP_SEGMENT:
            if command == PUSH_COMMAND:
                self.output.write(self._translate_push_temp(index))
            if command == POP_COMMAND:
                self.output.write(self._translate_pop_temp(index))

        elif segment == POINTER_SEGMENT:
            if command == PUSH_COMMAND:
                self.output.write(self._translate_push_pointer(index))
            if command == POP_COMMAND:
                self.output.write(self._translate_pop_pointer(index))

    def close(self) -> None:
        """Closes the output file."""
        # Your code goes here!
        self.output.close()
