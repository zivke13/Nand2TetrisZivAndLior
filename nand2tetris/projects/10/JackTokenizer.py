"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re
KEYWORDS = ["class", "method", "function", "constructor", "int", "boolean",
             "char", "void", "var", "static", "field", "let", "do", "if",
             "else", "while", "return", "true", "false", "null", "this"]

SYMBOLS = ["{", "}", "[", "]", "(", ")", ".", ",", ";", "+", "-", "*", "/",
            "&", "|", "<", ">", "=", "~"]


KEYWORD = "keyword"
SYMBOL = "symbol"
IDENTIFIER = "identifier"
INT_CONST = "int_const"
STRING_CONST = "string_const"


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is:
        # input_lines = input_stream.read().splitlines()
        self.input_lines = input_stream.read().splitlines()
        self.remove_spaces()
        self.remove_backslash()
        self.input_lines = [line for line in self.input_lines if line]
        self.input_tokens = []
        self.split_to_token()
        self.i = 0
        self.current = self.input_tokens[0]


    def remove_spaces(self):
        """
        delete the spaces from the input lines
        :return:
        """
        for i in range(0, len(self.input_lines), 1):
            self.input_lines[i] = self.input_lines[i].strip()

    def remove_backslash(self):
        for i in range(0, len(self.input_lines), 1):
            split_string = self.input_lines[i].split("//", 1)
            self.input_lines[i] = split_string[0]
            split_string = self.input_lines[i].split("/*", 1)
            self.input_lines[i] = split_string[0]
            split_string = self.input_lines[i].split("*", 1)
            self.input_lines[i] = split_string[0]

    def split_line_to_token(self, line):
        identifiers = '\w+'
        integers = '\d+'
        strings = '\".*\"'
        keywords = ('class|method|function|constructor|int|boolean|char|void|'
                         'var|static|field|let|do|if|else|while|return|true|false|'
                         'null|this')
        symbols = '{|}|\[|\]|\(|\)|\.|,|;|\+|-|\*|\/|&|\||<|>|=|~'
        composed = r'({}|{}|{}|{}|{})'.format(identifiers, integers, strings, keywords, symbols)
        return re.findall(composed, line)

    def split_to_token(self):
        for line in self.input_lines:
            split_token = self.split_line_to_token(line)
            self.input_tokens = self.input_tokens + split_token

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        if self.i < len(self.input_tokens) - 1:
            return True
        return False

        # Your code goes here!
        pass

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.i += 1
        self.current = self.input_tokens[self.i]

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.current in SYMBOLS:
            return SYMBOL

        if self.current in KEYWORDS:
            return KEYWORD

        if re.match("^\".*\"$", self.current):
            return STRING_CONST

        if re.match("^\d+$", self.current):
            return INT_CONST

        if re.match("^\w+$", self.current):
            return IDENTIFIER

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        if self.current in SYMBOLS:
            return self.current.upper
        else:
            return None
        # Your code goes here!
        pass

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        # Your code goes here!
        return self.current
        pass

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        return self.current
        pass

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        return self.current
        pass

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        return self.current
        pass
