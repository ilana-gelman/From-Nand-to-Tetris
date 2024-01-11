"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
# from os import stat
import typing

import re
from VMWriter import VMWriter
from SymbolTable import SymbolTable

BINARY_OP = re.compile(r"[+\-*/&|<>=]")
UNARY_OP = re.compile(r'[-~^#]')
KEYWORD_CONSTANT = re.compile(r'true|false|null|this')
CLASS_VAR_DEC = ('field', 'static')
CONSTANTS = ('integerConstant', 'stringConstant')
SUBROUTINE_NAMES = ('constructor', 'function', 'method')
TYPES = ('int', 'char', 'boolean')
BINARY_OPERATORS_DICT = {'+': 'add', '-': 'sub', '*': 'call Math.multiply 2',
                         '/': 'call Math.divide 2', '&': 'and', '|': 'or', '<': 'lt',
                         '>': 'gt', '=': 'eq'}
OS_METHODS = ('Memory', 'Screen', 'Array', 'Output', 'Keyboard', 'String', 'Math', 'Sys')

UNARY_OPERATORS_DICT = {'-': 'neg', '~': 'not', '^': 'shiftleft', '#': 'shiftright'}


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    label_counter = 1

    def __init__(self, input_stream: typing.TextIO, output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!o
        self.tokenizer = input_stream.read().splitlines()
        self.vm_writer = VMWriter(output_stream)
        self.symbol_table = SymbolTable()
        self.index = 0
        self.token = self.tokenizer[0].split(' ')
        self.class_name = None

        self.is_void_subroutine = False

    @staticmethod
    def get_current_label():
        CompilationEngine.label_counter = CompilationEngine.label_counter + 1
        return f"L{CompilationEngine.label_counter}"

    def advance(self, n):
        for i in range(n):
            if self.index < len(self.tokenizer) - 1:
                self.index += 1
                self.token = self.tokenizer[self.index].split(' ')
        return self.token[1]

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!

        self.class_name = self.advance(1)
        self.advance(2)
        self.compile_class_var_dec()

        self.compile_subroutine()
        self.advance(1)

    def add_args_to_symbol_table(self):
        arg_type, arg_name = self.token[1], self.advance(1)
        self.advance(1)
        self.symbol_table.define(arg_name, arg_type, 'ARG')
        while self.token[1] == ',':
            arg_type, arg_name = self.advance(1), self.advance(1)
            self.symbol_table.define(arg_name, arg_type, 'ARG')
            self.advance(1)

    def get_symbol_table_values(self):
        kind, val_type, val_name = self.token[1].upper(), self.advance(1), self.advance(1)
        return val_name, val_type, kind

    def add_decs_to_symbol_table(self):
        var_name, var_type, kind = self.get_symbol_table_values()
        self.advance(1)  # variableName -> , or ;
        self.symbol_table.define(var_name, var_type, kind.upper())
        while self.token[1] == ',':
            self.advance(1)
            self.symbol_table.define(self.token[1], var_type, kind.upper())
            self.advance(1)

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        while self.token[1] in CLASS_VAR_DEC:
            self.add_decs_to_symbol_table()
            self.advance(1)

    def handle_constructor(self):
        self.vm_writer.write_push('CONST', self.symbol_table.var_count('FIELD'))
        self.vm_writer.write_call('Memory.alloc', 1)
        self.vm_writer.write_pop('POINTER', 0)  # anchors this at the base address

    def handle_method(self):
        self.vm_writer.write_push('ARG', 0)
        self.vm_writer.write_pop('POINTER', 0)  # anchors this at the base address

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        # Your code goes here!
        if len(self.token) > 1 and self.token[1] in SUBROUTINE_NAMES:
            self.symbol_table.start_subroutine()
            subroutine_type, return_type, func_name = self.token[1], \
                                                      self.advance(1), \
                                                      self.class_name + "." + self.advance(1)
            self.is_void_subroutine = True if return_type == 'void' else False
            self.is_method_subroutine = True if subroutine_type == 'method' else False
            self.advance(2)  # func_name -> ( ->parameter list


            if subroutine_type == 'method':
                self.symbol_table.define('this', self.class_name, 'ARG')
            self.compile_parameter_list()  # parameter list -> ) -> {
            self.advance(1)  # { -> local variables declaration
            self.compile_var_dec()
            self.vm_writer.write_function(func_name, self.symbol_table.var_count("VAR"))
            if subroutine_type == 'constructor':
                self.handle_constructor()
            if subroutine_type == 'method':
                self.handle_method()

            self.compile_statements()
            self.advance(1)  # } ->next token
            self.compile_subroutine()

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        # Your code goes here!
        if self.token[1] != ')':
            self.add_args_to_symbol_table()
        self.advance(1)

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        while self.token[1] == 'var':
            self.add_decs_to_symbol_table()
            self.advance(1)

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        # Your code goes here!

        statements = {'let': self.compile_let, 'if': self.compile_if,
                      'while': self.compile_while, 'do': self.compile_do,
                      'return': self.compile_return}

        if len(self.token) > 1 and self.token[1] in statements.keys():
            statements[self.token[1]]()
            self.compile_statements()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        self.advance(1)  # do -> identifier
        self.handle_identifier_possibilities()
        self.advance(2)  # ) -> ; -> next token
        self.vm_writer.write_pop("TEMP", 0)

    def get_fixed_segment(self):
        segment = self.symbol_table.kind_of(self.token[1])
        segment = 'THIS' if segment == 'FIELD' else segment
        return 'LOCAL' if segment == 'VAR' else segment

    def handle_subroutine_call_expression(self, identifier, symbol):
        n_args = 0
        if symbol == '(':
            self.advance(2)  # ( -> ) or expression list
            self.vm_writer.write_push("POINTER", 0)
            n_args = self.compile_expression_list()
            self.vm_writer.write_call(self.class_name + "." + identifier, n_args + 1)

        if symbol == '.':
            segment = self.get_fixed_segment()
            class_name = self.symbol_table.type_of(self.token[1])
            if segment != '':  # method
                index = self.symbol_table.index_of(self.token[1])
                self.vm_writer.write_push(segment, index)
                n_args = 1
            else:  # ClassName.subroutineName(..) ClassName not in symbol table. such as OS classes
                class_name = self.token[1]

            identifier = self.advance(2)  # deAlloc
            self.advance(2)
            n_args = n_args + self.compile_expression_list()
            self.vm_writer.write_call(class_name + "." + identifier, n_args)

    def handle_array_expression(self):
        segment = self.get_fixed_segment()
        index = self.symbol_table.index_of(self.token[1])
        self.advance(1)
        self.handle_array_access(segment, index)
        self.vm_writer.write_pop('POINTER', 1)
        self.vm_writer.write_push('THAT', 0)

    def handle_identifier_possibilities(self):
        next_token = self.tokenizer[self.index + 1].split(' ')[1]
        cur_token = self.token[1]
        if next_token == '[':
            self.handle_array_expression()
        elif next_token == '(' or next_token == '.':
            self.handle_subroutine_call_expression(cur_token, next_token)
        else:
            kind, index = self.get_fixed_segment(), self.symbol_table.index_of(cur_token)
            self.vm_writer.write_push(kind, index)

    def handle_array_access(self, segment, index):
        self.vm_writer.write_push(segment, index)
        segment, index = 'THAT', 0
        self.advance(1)  # [ -> expression
        self.compile_expression()
        self.vm_writer.write_arithmetic('ADD')
        return segment, index

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
        self.advance(1)  # let -> varName
        segment = self.get_fixed_segment()
        index = self.symbol_table.index_of(self.token[1])
        self.advance(1)  # varName -> [ ?
        is_array = self.token[1] == '['
        if is_array:
            segment, index = self.handle_array_access(segment, index)
            self.advance(1)  # varName -> [
        self.advance(1)  # = -> expression | [ -> expression
        self.compile_expression()
        if is_array:
            self.vm_writer.write_pop('TEMP', 0)  # Store assigned value in temp
            self.vm_writer.write_pop('POINTER', 1)  # Restore destination
            self.vm_writer.write_push('TEMP', 0)  # Restore assigned value
        self.vm_writer.write_pop(segment, index)

        self.advance(1)  # ; -> next token

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        self.advance(2)  # while -> ( -> expression
        label1, label2 = self.get_current_label(), self.get_current_label()
        self.vm_writer.write_label(label1)
        self.compile_expression()
        self.vm_writer.write_arithmetic("NOT")
        self.vm_writer.write_if(label2)
        self.advance(2)  # ) -> { -> statements
        self.compile_statements()
        self.vm_writer.write_goto(label1)
        self.vm_writer.write_label(label2)
        self.advance(1)  # statements -> } -> next token

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        self.advance(1)  # return -> exp or ;
        if self.is_term():
            self.compile_expression()
        elif self.is_void_subroutine:
            self.vm_writer.write_push("CONST", 0)
        self.vm_writer.write_return()
        self.advance(1)  # ; -> next token

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        self.advance(2)  # if -> ( -> expression
        self.compile_expression()
        self.vm_writer.write_arithmetic('NOT')
        self.advance(2)  # ) -> { -> statement1 or statement2
        label1, label2 = self.get_current_label(), self.get_current_label()
        self.vm_writer.write_if(label1)
        self.compile_statements()  # statement1
        self.advance(1)  # } -> else
        is_else = True if self.token[1] == 'else' else False

        if is_else:
            self.advance(2)  # else  -> { -> statements2
            self.vm_writer.write_goto(label2)
            self.vm_writer.write_label(label1)
            self.compile_statements()  # statement2
            self.advance(1)  # } -> next token
        if not is_else:
            self.vm_writer.write_label(label1)
        else:
            self.vm_writer.write_label(label2)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # x + ( g(2,y,-z) * 5 )  g(2,y,-z) * 5

        self.compile_term()
        self.advance(1)
        if BINARY_OP.match(self.token[1]):
            operator = self.token[1]
            self.advance(1)
            self.compile_expression()
            self.vm_writer.write_arithmetic(BINARY_OPERATORS_DICT[operator])

    def handle_string_constant_assignment(self, string_constant):
        self.vm_writer.write_push("CONST", len(string_constant))
        self.vm_writer.write_call('String.new', 1)
        for i in range(len(string_constant)):
            self.vm_writer.write_push("CONST", ord(string_constant[i]))
            self.vm_writer.write_call('String.appendChar', 2)

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
        type_of_term = self.token[0][1:-1]

        if type_of_term == 'integerConstant':
            self.vm_writer.write_push("CONST", int(self.token[1]))

        elif type_of_term == 'stringConstant':
            string_constant = " ".join(self.token[1:-1])
            self.handle_string_constant_assignment(string_constant)

        elif KEYWORD_CONSTANT.match(self.token[1]):
            n = 1 if self.token[1] == 'true' else 0
            segment = "POINTER" if self.token[1] == 'this' else "CONST"
            self.vm_writer.write_push(segment, n)
            if n == 1:
                self.vm_writer.write_arithmetic("NEG")

        elif type_of_term == 'identifier':
            self.handle_identifier_possibilities()

        elif UNARY_OP.match(self.token[1]):
            operator = self.token[1]
            self.advance(1)
            self.compile_term()
            self.vm_writer.write_arithmetic(UNARY_OPERATORS_DICT[operator])

        elif '(' in self.token[1]:
            self.advance(1)
            self.compile_expression()

    def is_term(self):
        return KEYWORD_CONSTANT.match(self.token[1]) or self.token[0][1:-1] in CONSTANTS \
               or '(' in self.token[1] or UNARY_OP.match(self.token[1]) or self.token[0][1:-1] == 'identifier'

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        count = 0
        if self.is_term():
            self.compile_expression()
            count = count + 1
            while ',' in self.token[1]:
                self.advance(1)
                self.compile_expression()
                count = count + 1
        return count
