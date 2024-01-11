"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

import typing
import re

IDENTIFIER = re.compile("[a-z]|[A-Z]|_\w*")
KEYWORDS = {'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean',
            'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'}
SYMBOLS = r'#^(){}[],;=.+-*/&|~<>'

DELIMITERS = re.compile(r'([\(\)\[\]\{\}\,\;\=\.\+\-\*\/\&\|\~\<\>\s]|(?:"[^"]*"))')


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
        self.input_lines = input_stream.read().splitlines()
        self.tokens_lst = self.tokenize()
        self.cur_token = None
        self.cur_token_num = 0

    def ignore_multiline_comments(self, current, i):
        """
        advances the current line until */ is met
        """
        if '*/' in current:
            return self.input_lines[i], i
        return self.ignore_multiline_comments(self.input_lines[i].strip(), i + 1)

    def tokenize(self):
        string_constant = ''
        i = 0
        token_list = list()
        # token_str = " ".join(self.input)
        while i < len(self.input_lines):
            # API COMMENTS
            current = self.input_lines[i]
            if '/**' in current:
                current, i = self.ignore_multiline_comments(self.input_lines[i].strip(), i)
            # if empty line
            if current:
                # replace string constants temporarily
                if current.count('"') == 2:
                    start, end = '\"', '\";'
                    string_constant = '\"' + current[current.find(start) + len(start):current.rfind(end)] + '\"'
                    current = current.replace(string_constant, '@')
                # in-line comments /* */
                while '/*' in current:
                    current, i = self.handle_in_line_comments(current, i)

                current = current.split('//')[0].replace('@', string_constant) if string_constant else \
                    current.split('//')[0]
                token_list.append(current)
            i += 1
        file_string = " ".join(token_list)
        return [token for token in DELIMITERS.split(file_string) if token not in ('', ' ')]

    def handle_in_line_comments(self, line: str, i: int):
        """
        handle comments /* */
        """
        start = line.find('/*')
        end = line.find('*/')
        if start == -1 and end == -1:
            return line
        if start != -1 and end == -1:
            return self.ignore_multiline_comments(line, i)
        in_line_comment = line[start: end + 2]
        line = line.replace(in_line_comment, '')
        return self.handle_in_line_comments(line, i), i

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # Your code goes here!
        return self.cur_token_num != len(self.tokens_lst)

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token.
        This method should be called if has_more_tokens() is true.
        Initially there is no current token.
        """
        # Your code goes here!
        if self.has_more_tokens():
            self.cur_token = self.tokens_lst[self.cur_token_num]
            self.cur_token_num += 1

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Your code goes here!
        if self.cur_token in KEYWORDS:
            return "KEYWORD"
        if self.cur_token in SYMBOLS:
            return "SYMBOL"
        if self.cur_token.isnumeric() and 0 <= int(self.cur_token) <= 32767:
            return "INT_CONST"
        if self.cur_token[0] == '"':
            return "STRING_CONST"
        if IDENTIFIER.match(self.cur_token) is not None:
            return 'IDENTIFIER'

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT",
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO",
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        # Your code goes here!
        if self.token_type() == "KEYWORD":
            return self.cur_token.upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        # Your code goes here!
        if self.token_type() == "SYMBOL":
            return self.cur_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        # Your code goes here!
        if self.token_type() == "IDENTIFIER":
            return self.cur_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        # Your code goes here!
        if self.token_type() == "INT_CONST":
            return int(self.cur_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        # Your code goes here!
        if self.token_type() == "STRING_CONST":
            return self.cur_token[1:-1]
