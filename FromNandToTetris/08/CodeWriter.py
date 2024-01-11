"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""
    call_counter = 1
    is_init_written = False
    label_num = 0

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        self.output = output_stream
        self.filename = None
        self.func_name = 'main'

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.filename = filename

    # Part 2
    def writeInit(self):
        if not CodeWriter.is_init_written:
            self.output.write(f'@256\nD=A\n@SP\nM=D\n')
            self.writeCall('Sys.init', 0)
            CodeWriter.is_init_written = True

    def writeLabel(self, label: str) -> None:
        self.output.write(f'({self.func_name}${label})\n')

    def writeGoto(self, label: str) -> None:
        self.output.write(f'@{self.func_name}${label}\n0;JMP\n')

    def writeIf(self, label: str) -> None:
        self.output.write(f'@SP\nAM=M-1\nD=M\n@{self.func_name}${label}\nD;JNE\n')

    def writeCall(self, functionName: str, numArgs: int) -> None:
        return_address = 'return_' + functionName + "." + str(CodeWriter.call_counter)
        self.output.write(f'@{return_address}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
        self.output.write(f'@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
        self.output.write(f'@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
        self.output.write(f'@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
        self.output.write(f'@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n')
        self.output.write(f'@{str(numArgs + 5)}\nD=A\n@SP\nD=M-D\n@ARG\nM=D\n')
        self.output.write(f'@SP\nD=M\n@LCL\nM=D\n')
        self.output.write(f'@{functionName}\n0;JMP\n')
        self.output.write(f'({return_address})\n')
        CodeWriter.call_counter += 1

    def writeReturn(self) -> None:
        self.output.write(f'@LCL\nD=M\n@R15\nM=D\n')
        self.restoreSegment('R14', '5')
        self.write_push_pop('C_POP', 'argument', 0)
        self.output.write(f'@ARG\nD=M+1\n@SP\nM=D\n')
        self.restoreSegment('THAT', '1')
        self.restoreSegment('THIS', '2')
        self.restoreSegment('ARG', '3')
        self.restoreSegment('LCL', '4')
        self.output.write(f'@R14\nA=M\n0;JMP\n')

    def restoreSegment(self, segment, index):
        self.output.write(f'@{str(index)}\nD=A\n@R15\nA=M-D\nD=M\n@{segment}\nM=D\n')

    def writeFunction(self, functionName: str, numLocals: int) -> None:
        self.func_name = functionName
        self.output.write(f'({functionName})\n')
        for i in range(numLocals):
            self.output.write(f'@SP\nA=M\nM=0\n@SP\nM=M+1\n')

    # Part 1
    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        # Your code goes here!
        comps = {'eq': 'JEQ', 'gt': 'JGT', 'lt': 'JLT'}
        ops = {'add': '+', 'sub': '-', 'neg': '-', 'shiftleft': '<<',
               'shiftright': '>>', 'and': '&', 'or': '|', 'not': '!'}
        if command in comps.keys():
            self.write_comp(comps[command])
            CodeWriter.label_num += 1
        if command in ops.keys():
            self.write_ops(ops[command], command)

    def write_comp(self, jmp):
        """
        writes assembly code for the commands:eq,gt,lt
        Args:
        jmp- 'JEQ' or 'JGT'or 'JLT' 
        """
        i = str(CodeWriter.label_num)
        m1 = -1 if jmp == 'JLT' else 0  # pos_neg
        m2 = -1 if jmp == 'JGT' else 0  # neg_pos
        if jmp != 'JEQ':
            self.output.write(f'@SP\nAM=M-1\nD=M\n@POS.{i}\nD;JGT\n@NEG.{i}\n0;JMP\n')
            self.output.write(f'(POS.{i})\n@SP\nA=M-1\nD=M\n@EQSIGN.{i}\nD;JGT\n@POSNEG.{i}\n0;JMP\n')
            self.output.write(f'(NEG.{i})\n@SP\nA=M-1\nD=M\n@NEGPOS.{i}\nD;JGT\n@EQSIGN.{i}\n0;JMP\n')

            self.output.write(f'(EQSIGN.{i})\n@SP\n')
            self.output.write(f'A=M\nD=M\n@SP\nA=M-1\nD=M-D\nM=-1\n@END.{i}\nD;{jmp}\n')
            self.output.write(f'@SP\nA=M-1\nM=0\n@END.{i}\n0;JMP\n')

            self.output.write(f'(POSNEG.{i})\n@SP\nA=M-1\nM={str(m1)}\n')
            self.output.write(f'@END.{i}\n0;JMP\n')
            self.output.write(f'(NEGPOS.{i})\n@SP\nA=M-1\nM={str(m2)}\n')
        else:
            self.output.write(f'@SP\nAM=M-1\n')
            self.output.write(f'D=M\nA=A-1\nD=M-D\nM=-1\n@END.{i}\nD;{jmp}\n')
            self.output.write(f'@SP\nA=M-1\nM=0\n')
        self.output.write(f'(END.{i})\n')

    def write_ops(self, op, key):
        """
        writes assembly code for the opertors
        Args:
        op- the operator
        key- the command
        """
        self.output.write(f'@SP\nM=M-1\n')
        if key in {'add', 'sub', 'and', 'or'}:
            self.output.write(f'@SP\nA=M\nD=M\n@SP\nM=M-1\n')
        self.output.write(self.do_operator(op, 'M', key) + '@SP\nM=M+1\n')

    def do_operator(self, op, ch, key):
        """
        returns assembly code for c-instruction
        """
        to_write = '@SP\nA=M\n'
        if 'shift' in key:
            to_write += f'{ch}=M{op}\n'
        elif 'not' == key or 'neg' == key:
            to_write += f'{ch}={op}M\n'
        else:
            to_write += f'{ch}=M{op}D\n'
        return to_write

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        static_fixed = self.filename + '.' + str(index)
        segments = {'constant': None, 'local': 'LCL', 'argument': 'ARG',
                    'this': 'THIS', 'that': 'THAT',
                    'pointer': 'PTR', 'temp': 'TMP', 'static': static_fixed}
        if segment in segments.keys():
            if command == 'C_PUSH':
                self.write_push(segments[segment], index)
            elif command == 'C_POP' and segment is not None:
                self.write_pop(segments[segment], index)

    def write_push(self, segment, index):
        """
        writes the push command in assembly code
        """
        base = 5 if segment == 'TMP' else 3
        if segment is None:  # relevant for push only
            self.output.write(f'@{index}\nD=A\n')
        elif self.filename in segment:  # pointer,static
            self.output.write(f'@{segment}\nD=M\n')
        elif segment == 'TMP' or segment == 'PTR':  # temp or pointer
            self.output.write(f'@{base + index}\nD=M\n')
        else:
            self.output.write(f'@{index}\nD=A\n@{segment}\nA=D+M\nD=M\n')  # local,argument,this,that
        self.output.write(f'@SP\nA=M\nM=D\n@SP\nM=M+1\n')

    def write_pop(self, segment, index):
        """
        writes the pop command in assembly code
        """
        base = 5 if segment == 'TMP' else 3
        if self.filename in segment:  # static  
            self.output.write(f'@SP\nAM=M-1\nD=M\n')
            self.output.write(f'@{segment}\nM=D\n')
        elif segment == 'TMP' or segment == 'PTR':  # temp or pointer
            self.output.write(f'@SP\nAM=M-1\nD=M\n')
            self.output.write(f'@{base + index}\nM=D\n')
        else:
            self.output.write(
                f'@{index}\nD=A\n@{segment}\nA=M+D\nD=A\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n')
            # local,argument,this,that


