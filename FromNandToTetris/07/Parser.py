"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


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
        self.cur_line_num = 0
        self.cur_command = None

    def remove_white_trails_and_comments(self):
        self.cur_command = self.cur_command.strip()
        self.cur_command = self.cur_command.split('/')[0].strip()

    def is_command(self, index):
        return not (not (self.input_lines[index]) or self.input_lines[index].strip()[0] == '/')

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # Your code goes here!
        for i in range(self.cur_line_num, len(self.input_lines)):
            if self.is_command(i):
                return True
        return False

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        # Your code goes here!
        if self.has_more_commands():
            while not (self.is_command(self.cur_line_num)):
                self.cur_line_num += 1

            self.cur_command = self.input_lines[self.cur_line_num]
            self.remove_white_trails_and_comments()
            self.cur_line_num += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        # Your code goes here!
        arithmetic_set = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not", "shiftleft", "shiftright"}
        arg1 = self.cur_command.split(' ')[0]
        if arg1 in arithmetic_set:
            return 'C_ARITHMETIC'
        if arg1 == 'push':
            return 'C_PUSH'
        if arg1 == 'pop':
            return 'C_POP'

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        # Your code goes here!
        if self.command_type() == 'C_ARITHMETIC':
            return self.cur_command
        return self.cur_command.split(' ')[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        # Your code goes here!
        if self.command_type() == 'C_PUSH' or self.command_type() == 'C_POP':
            return int(self.cur_command.split(' ')[2])
