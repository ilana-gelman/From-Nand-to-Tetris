"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from os import stat
import typing
import re

op = re.compile(r"[+\-*/&|<>=]")
unaryOp = re.compile(r'[-~^#]')
keywordConstant = re.compile(r'true|false|null|this')
class_var_dec = ['field', 'static']
constants = ['integerConstant', 'stringConstant']
subroutine_names = ['constructor', 'function', 'method']
types = ['int', 'char', 'boolean']


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: typing.TextIO,
                 output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        self.token_file = input_stream.read().splitlines()
        self.out = output_stream
        # self.written = True
        self.index = 1
        self.token = self.token_file[1].split(' ')
        # self.class_name = None

    def write_open_label(self, label):
        self.out.write(f"<{label}>\n")
        self.get_next_token()

    def write_closing_label(self, label):
        self.out.write(f"</{label}>\n")
        self.get_next_token()

    def get_next_token(self):
        # print(self.index)
        if self.index < len(self.token_file):
            self.token = self.token_file[self.index].split(' ')
            self.index += 1

    def write_next_keyword(self, labels):
        if 'keyword' == self.token[0][1:-1] and self.token[1] in labels:
            self.out.write(" ".join(self.token) + '\n')
            self.get_next_token()

    def write_next_id_zero_or_more(self):
        if self.token[1] == ',' or 'identifier' == self.token[0][1:-1]:
            self.out.write(" ".join(self.token) + '\n')
            self.get_next_token()
            self.write_next_id_zero_or_more()

    def write_next_symbol(self, elem):
        if 'symbol' == self.token[0][1:-1] and elem == self.token[1]:
            self.out.write(" ".join(self.token) + '\n')
            self.get_next_token()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        self.out.write(f"<class>\n")
        self.get_next_token()
        # self.class_name = self.token[1]
        # types.append(self.class_name)
        self.write_next_keyword(['class'])
        self.write_next_id_zero_or_more()
        self.write_next_symbol('{')
        self.compile_class_var_dec()
        self.compile_subroutine()
        self.write_next_symbol('}')
        self.out.write(f"</class>\n")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        while self.token[1] in class_var_dec:
            self.out.write(f"<classVarDec>\n")
            self.write_next_keyword(class_var_dec)
            self.write_next_keyword(types)
            self.write_next_id_zero_or_more()  # varName (',' varName)*
            self.write_next_symbol(';')  # ;
            self.out.write(f"</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        # Your code goes here!

        if len(self.token) > 1 and self.token[1] in subroutine_names:
            self.out.write(f"<subroutineDec>\n")
            self.write_next_keyword(subroutine_names)
            self.write_next_keyword(['void', 'int', 'char', 'boolean'])
            self.write_next_id_zero_or_more()
            self.write_next_symbol('(')
            self.out.write(f"<parameterList>\n")
            self.compile_parameter_list()
            self.out.write(f"</parameterList>\n")
            self.write_next_symbol(')')
            # subrotinebody
            self.out.write(f"<subroutineBody>\n")
            self.write_next_symbol('{')
            self.compile_var_dec()
            self.out.write(f"<statements>\n")
            self.compile_statements()
            self.out.write(f"</statements>\n")
            self.write_next_symbol('}')
            self.out.write(f"</subroutineBody>\n")
            self.out.write(f"</subroutineDec>\n")
            self.compile_subroutine()

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # Your code goes here!
        if self.token[1] == ',' or self.token[1] in types or "identifier" == self.token[0][1:-1]:
            self.write_next_keyword(types)
            self.write_next_id_zero_or_more()
            self.compile_parameter_list()

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        if self.token[1] == 'var':
            self.out.write(f"<varDec>\n")
            self.write_next_keyword(['var'])
            self.write_next_keyword(types)
            self.write_next_id_zero_or_more()
            self.write_next_symbol(';')
            self.out.write(f"</varDec>\n")
            self.compile_var_dec()

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
        self.out.write(f"<doStatement>\n")
        self.write_next_keyword(['do'])
        self.handle_identifier_possibilities()
        self.write_next_symbol(';')
        self.out.write(f"</doStatement>\n")

    def handle_identifier_possibilities(self):
        next = self.token_file[self.index].split(' ')
        if next[1] == '(':
            self.write_next_id_zero_or_more()  # subroutine name
            self.write_next_symbol('(')
            self.out.write(f"<expressionList>\n")
            self.compile_expression_list()
            self.out.write(f"</expressionList>\n")
            self.write_next_symbol(')')
        elif next[1] == '.':
            self.write_next_id_zero_or_more()  # className|varName
            self.write_next_symbol('.')
            self.write_next_id_zero_or_more()
            self.write_next_symbol('(')
            self.out.write(f"<expressionList>\n")
            self.compile_expression_list()
            self.out.write(f"</expressionList>\n")
            self.write_next_symbol(')')
        elif next[1] == '[':
            self.write_next_id_zero_or_more()
            self.write_next_symbol('[')
            self.out.write(f"<expression>\n")
            self.compile_expression()
            self.out.write(f"</expression>\n")
            self.write_next_symbol(']')
        else:
            if self.token[0][1:-1] == 'identifier':
                self.out.write(" ".join(self.token) + '\n')
                self.get_next_token()

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
        # Your code goes here!
        self.out.write(f"<letStatement>\n")
        self.write_next_keyword(['let'])
        self.write_next_id_zero_or_more()
        if self.token[1] == '[':
            self.write_next_symbol('[')
            self.out.write(f"<expression>\n")
            self.compile_expression()
            self.out.write(f"</expression>\n")
            self.write_next_symbol(']')
        self.write_next_symbol('=')
        self.out.write(f"<expression>\n")
        self.compile_expression()
        self.out.write(f"</expression>\n")
        self.write_next_symbol(';')
        self.out.write(f"</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        self.out.write(f"<whileStatement>\n")
        self.write_next_keyword(['while'])
        self.write_next_symbol('(')
        self.out.write(f"<expression>\n")
        self.compile_expression()
        self.out.write(f"</expression>\n")
        self.write_next_symbol(')')
        self.write_next_symbol('{')
        self.out.write(f"<statements>\n")
        self.compile_statements()
        self.out.write(f"</statements>\n")
        self.write_next_symbol('}')
        self.out.write(f"</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        self.out.write(f"<returnStatement>\n")
        self.write_next_keyword(['return'])
        if self.is_term():
            self.out.write(f"<expression>\n")
            self.compile_expression()
            self.out.write(f"</expression>\n")
        self.write_next_symbol(';')
        self.out.write(f"</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        self.out.write(f"<ifStatement>\n")
        self.write_next_keyword(['if'])
        self.write_next_symbol('(')
        self.out.write(f"<expression>\n")
        self.compile_expression()
        self.out.write(f"</expression>\n")
        self.write_next_symbol(')')
        self.write_next_symbol('{')
        self.out.write(f"<statements>\n")
        self.compile_statements()
        self.out.write(f"</statements>\n")
        self.write_next_symbol('}')
        if self.token[1] != 'else':
            self.out.write(f"</ifStatement>\n")
        else:
            self.write_next_keyword(['else'])
            self.write_next_symbol('{')
            self.out.write(f"<statements>\n")
            self.compile_statements()
            self.out.write(f"</statements>\n")
            self.write_next_symbol('}')
            self.out.write(f"</ifStatement>\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # Your code goes here!
        self.out.write(f"<term>\n")
        self.compile_term()
        self.out.write(f"</term>\n")
        if op.match(self.token[1]):
            self.write_next_symbol(self.token[1])
            self.compile_expression()

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
        # Your code goes here!
        # print(self.token)
        if keywordConstant.match(self.token[1]) or self.token[0][1:-1] in constants:
            # print(self.token)
            self.out.write(" ".join(self.token) + '\n')
            self.get_next_token()
        elif '(' in self.token[1]:
            # print("FOUND2")
            self.write_next_symbol('(')
            self.out.write(f"<expression>\n")
            self.compile_expression()
            self.out.write(f"</expression>\n")
            self.write_next_symbol(')')
        elif unaryOp.match(self.token[1]):
            # print("FOUND3")
            self.write_next_symbol(self.token[1])
            self.out.write(f"<term>\n")
            self.compile_term()
            self.out.write(f"</term>\n")
        elif self.token[0][1:-1] == 'identifier':
            # print("FOUND4")
            # print(self.token)
            self.handle_identifier_possibilities()
            # print(self.token)

    def is_term(self):
        return keywordConstant.match(self.token[1]) or self.token[0][1:-1] in constants \
               or '(' in self.token[1] or unaryOp.match(self.token[1]) or self.token[0][1:-1] == 'identifier'

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        if self.is_term():
            self.out.write(f"<expression>\n")
            self.compile_expression()
            self.out.write(f"</expression>\n")
            if ',' in self.token[1]:
                self.write_next_symbol(',')
                self.compile_expression_list()
