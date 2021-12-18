"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from contextlib import contextmanager

from xml.etree.ElementTree import Element, tostring
from xml.dom import minidom

from JackTokenizer import JackTokenizer


CLASS_VAR_DEC_TYPES = ["field", "static"]
SUBROUTINE_DEC_TYPES = ["constructor", "function", "method"]
VAR_DEC_TYPE = "var"
IDENTIFIER_TYPE = "identifier"
ELSE_TYPE = "else"
COMMA = ','
OP = ["+", "-", "*", "/", "&", "|", "<", ">", "="]


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: typing.TextIO, output_stream: typing.TextIO, tokenizer: JackTokenizer) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.tokenizer = tokenizer
        self.root = Element('class')
        self.current_element = self.root
        self.tag_count = 0

        self.statement_type_to_function = {
            "do": self.compile_do,
            "let": self.compile_let,
            "while": self.compile_while,
            "return": self.compile_return,
            "if": self.compile_if
        }

    def compile_class(self) -> None:
        """Compiles a complete class."""
        for _ in range(3):
            self._write_token()

        while self.tokenizer.string_val() in CLASS_VAR_DEC_TYPES:
            with self._write_tag("classVarDec"):
                self.compile_class_var_dec()

        while self.tokenizer.string_val() in SUBROUTINE_DEC_TYPES:
            with self._write_tag("subroutineDec"):
                self.compile_subroutine()

        self._write_token()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        while self.tokenizer.symbol() != ';':
            self._write_token()
        self._write_token()

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        for i in range(4):
            self._write_token()

        with self._write_tag("parameterList"):
            self.compile_parameter_list()
        self._write_token()

        with self._write_tag("subroutineBody"):
            self._write_token()
            while self.tokenizer.symbol() == VAR_DEC_TYPE:
                with self._write_tag("varDec"):
                    self.compile_var_dec()

            with self._write_tag("statements"):
                self.compile_statements()
            self._write_token()

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        while self.tokenizer.symbol() != ")":
            self._write_token()

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        while self.tokenizer.symbol() != ";":
            self._write_token()
        self._write_token()

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        while self.tokenizer.symbol() in self.statement_type_to_function:
            with self._write_tag(f"{self.tokenizer.symbol()}Statement"):
                self.statement_type_to_function[self.tokenizer.symbol()]()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        for i in range(5):
            self._write_token()

        with self._write_tag("expressionList"):
            self.compile_expression_list()
        for i in range(2):
            self._write_token()

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self._write_token()
        if self.tokenizer.token_type() == IDENTIFIER_TYPE:
            self._write_token()
        self._write_token()

        with self._write_tag("expression"):
            self.compile_expression()

        self._write_token()

    def compile_while(self) -> None:
        """Compiles a while statement."""
        for i in range(2):
            self._write_token()

        with self._write_tag("expression"):
            self.compile_expression()

        for i in range(2):
            self._write_token()

        with self._write_tag("statements"):
            self.compile_statements()

        self._write_token()

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self._write_token()

        if self.tokenizer.symbol() != ';':
            with self._write_tag("expression"):
                self.compile_expression()
        self._write_token()

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        for i in range(2):
            self._write_token()

        with self._write_tag("expression"):
            self.compile_expression()

        for i in range(2):
            self._write_token()

        with self._write_tag("statements"):
            self.compile_statements()

        self._write_token()

        if self.tokenizer.symbol() == ELSE_TYPE:
            for i in range(2):
                self._write_token()

            with self._write_tag("statements"):
                self.compile_statements()

            self._write_token()

    # 12
    def compile_expression(self) -> None:
        """Compiles an expression."""
        with self._write_tag("term"):
            self.compile_term()
        if self.tokenizer.symbol() in OP:
            self._write_token()
            with self._write_tag("term"):
                self.compile_term()
    # 13
    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        if self.tokenizer.symbol() == '(':
            self._write_token()
            with self._write_tag("expression"):
                self.compile_expression()
            self._write_token()
        else:
            self._write_token()
            if self.tokenizer.symbol() == '[':
                self._write_token()
                with self._write_tag("expression"):
                    self.compile_expression()
                self._write_token()

    # 14
    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        while self.tokenizer.symbol() != ")":
            with self._write_tag("expression"):
                self.compile_expression()
            if self.tokenizer.symbol() == COMMA:
                self._write_token()

    def write_to_file(self) -> None:
        xml = minidom.parseString(tostring(self.root)).toprettyxml(" " * 2)
        pretty_xml = '\n'.join(xml.splitlines()[1:])
        self.output_stream.write(pretty_xml)

    def _write_token(self) -> None:
        self.tag_count += 1
        new_element = Element(self.tokenizer.token_type())
        new_element.text = self.tokenizer.symbol()
        self.current_element.insert(self.tag_count, new_element)

        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()

    @contextmanager
    def _write_tag(self, tag_type: str) -> None:
        self.tag_count += 1
        current_element = self.current_element
        new_tag = Element(tag_type)
        self.current_element.insert(self.tag_count, new_tag)
        self.current_element = new_tag
        yield
        self.current_element = current_element
