"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

A_COMMAND = "A_COMMAND"
L_COMMAND = "L_COMMAND"
C_COMMAND = "C_COMMAND"

class Parser:
    """Encapsulates access to the input code. Reads and assembly language 
    command, parses it, and provides convenient access to the commands 
    components (fields and symbols). In addition, removes all white space and 
    comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is:
        # input_lines = input_file.read().splitlines()
        self.input_lines = input_file.read().splitlines()
        self.remove_spaces()
        self.remove_backSlesh()
        self.new_input_lines = []
        self.i = 0
        self.current = self.input_lines[0]

    def remove_spaces(self):
        """
        delete the spaces from the input lines
        :return:
        """
        for i in range(0,len(self.input_lines),1):
            self.input_lines[i] = self.input_lines[i].replace(" ", "")

    def remove_backSlesh(self):
        for i in range(0,len(self.input_lines),1):
            split_string = self.input_lines[i].split("//", 1)
            self.input_lines[i] = split_string[0]

    @property
    def line_number(self)-> int:
        return self.i

    def restart(self):
        self.i = 0
        self.current = self.input_lines[0]

    def remove_lines(self) -> None:
        del self.input_lines[self.i]
        self.current = self.input_lines[self.i]

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        if self.i < len(self.input_lines):
            return True
        else:
            return False
        pass

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        self.current = self.input_lines[self.i]
        self.i += 1
        pass

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if self.current[0] == '@':
            return A_COMMAND
        elif self.current[0] == '(':
            return L_COMMAND
        else:
            return C_COMMAND
        pass

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        if self.command_type() == A_COMMAND:
            return self.current[1:]
        elif self.command_type() == L_COMMAND:
            return self.current[1:-1]
        else:
            return self.current
        # Your code goes here!
        pass

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        currentArr = self.current.split(";")
        if len(currentArr) == 2:
            return currentArr[1]
        return ""
        pass

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        return self.current.split(";")[0].split("=")[-1]

        # Your code goes here!
        pass

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        currentArr = self.current.split("=")
        if len(currentArr) == 2:
            return currentArr[0]
        return ""
