"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
C_ARITHMETIC = "C_ARITHMETIC"
C_PUSH = "C_PUSH"
C_POP = "C_POP"
C_LABEL = "C_LABEL"
C_GOTO = "C_GOTO"
C_IF_GOTO = "C_IF_GOTO"
C_FUNCTION = "C_FUNCTION"
C_RETURN = "C_RETURN"
C_CALL = "C_CALL"
arithmetic = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not", "shiftright", "shiftleft"]

class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.input_lines = input_file.read().splitlines()
        self.remove_spaces()
        self.remove_backslash()
        self.input_lines = [line for line in self.input_lines if line]
        self.i = 0
        self.current = self.input_lines[0]
        self.current_split = self.current.split()

    def remove_spaces(self):
        """
        delete the spaces from the input lines
        :return:
        """
        for i in range(0,len(self.input_lines),1):
            self.input_lines[i] = self.input_lines[i].strip()

    def remove_backslash(self):
        for i in range(0,len(self.input_lines),1):
            split_string = self.input_lines[i].split("//", 1)
            self.input_lines[i] = split_string[0]

    @property
    def line_number(self) -> int:
        return self.i

    def restart(self):
        self.i = 0
        self.current = self.input_lines[0]

    def remove_line(self) -> None:
        del self.input_lines[self.i]
        self.current = self.input_lines[self.i]

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        if self.i < len(self.input_lines) - 1:
            return True
        return False


    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        self.i += 1
        self.current = self.input_lines[self.i]
        self.current_split = self.current.split()
        pass

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        if self.current_split[0] in arithmetic:
            return C_ARITHMETIC
        if self.current_split[0] == "return":
            return C_RETURN
        if self.current_split[0] == "push":
            return C_PUSH
        if self.current_split[0] == "pop":
            return C_POP
        if self.current_split[0] == "label":
            return C_LABEL
        if self.current_split[0] == "if-goto":
            return C_IF_GOTO
        if self.current_split[0] == "goto":
            return C_GOTO
        if self.current_split[0] == "function":
            return C_FUNCTION
        if self.current_split[0] == "call":
            return C_CALL


        # Your code goes here!
        pass

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        if self.command_type() == C_ARITHMETIC:
            return self.current_split[0]
        else:
            return self.current_split[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        return int(self.current_split[2])
