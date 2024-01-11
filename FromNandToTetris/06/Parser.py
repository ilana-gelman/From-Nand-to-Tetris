"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

class Parser:
    """Encapsulates access to the input code. Reads and assembly language 
    command, parses it, and provides convenient access to the commands 
    components (fields and symbols). In addition, removes all white space and 
    comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.
        Args: input_file (typing.TextIO): input file.
        """
        self.input_lines = input_file.read().splitlines()
        self.input_lines = [j.replace(' ', '') for j in self.input_lines if j.replace(' ', '') != '']
        self.remove_comments()
        self.cur_line_num = 0
        self.current_command_line_num = 0
        self.current_command = None

    def remove_comments(self):
        """
        remove all the comments in the file.
        """
        self.input_lines = [line for line in self.input_lines if line[0] != '/']
        for i in range(len(self.input_lines)):
            self.input_lines[i] = self.input_lines[i].split('/')[0]

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?
        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.cur_line_num != len(self.input_lines)

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        if self.has_more_commands():
            if self.input_lines[self.cur_line_num][0] != '(':
                self.current_command = self.input_lines[self.cur_line_num]
                self.current_command_line_num += 1
            else:
                self.current_command = self.input_lines[self.cur_line_num]

            self.cur_line_num += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if self.current_command[0] == '@':
            return "A_COMMAND"
        elif self.current_command[0] == '(':
            return "L_COMMAND"
        else:
            return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        # Your code goes here!
        if self.command_type() == 'A_COMMAND':
            return self.current_command[1:]

        if self.command_type() == 'L_COMMAND':
            return self.current_command[1:-1]

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() == 'C_COMMAND':
            if '=' in self.current_command:
                return self.current_command.split('=')[0]

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() == 'C_COMMAND':
            if '=' in self.current_command:
                split = self.current_command.split('=')
                if ';' in split[1]:
                    return split[1].split(';')[0]
                else:
                    return split[1]
            else:
                if ';' in self.current_command:
                    return self.current_command.split(';')[0]

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() == 'C_COMMAND':
            if ';' in self.current_command:
                return self.current_command.split(';')[1]
