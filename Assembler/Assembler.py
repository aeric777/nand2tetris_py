#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Compile Assembly code into Binary Machine code."""

__author__ = 'eric'

import getopt
import os
import sys


# ----------------------------------------------------------
# Description:
#   Compile assembly language into machine language(binary code)
#   .asm --> .hack (.bin)
# Input:
#   asm_list        - list of str that compose asm file
def assembler(asm_list):
    print('[Log]:\t--*  assembler  *--')
    # print('[Log]:\tasm_list:\n', asm_list)

    # build symbol table and replace all the symbol in .asm file with its corresponding numeric value
    build_symbol_table = SymbolTable(asm_list)  # instantiate SymbolTable
    no_symbol_list = build_symbol_table.get_no_symbol_list()

    # parser .asm code line by line into machine code(binary)
    parser = Parser(no_symbol_list)  # instantiate Parser
    bin_list = parser.get_bin_list()
    # print('[Log]:\tparsed file:\n', bin_list)

    return bin_list


# ----------------------------------------------------------
# Description:
#   build symbol table and replace all the symbol in .asm file with its corresponding numeric value
class SymbolTable(object):
    def __init__(self, asm_list):
        self.asm_list = asm_list
        self.no_comment_list = []
        self.no_symbol_list = []
        # add predefined symbol into symbol_table
        self.symbol_table = {
            'SP': '0',
            'LCL': '1',
            'ARG': '2',
            'THIS': '3',
            'THAT': '4',
            'R0': '0',
            'R1': '1',
            'R2': '2',
            'R3': '3',
            'R4': '4',
            'R5': '5',
            'R6': '6',
            'R7': '7',
            'R8': '8',
            'R9': '9',
            'R10': '10',
            'R11': '11',
            'R12': '12',
            'R13': '13',
            'R14': '14',
            'R15': '15',
            'SCREEN': '16384',
            'KBD': '24576'}

        # main process
        self.remove_comment()
        self.proc_label()
        self.proc_variable()
        self.replace_symbol()

    # ----------------------------------------------------------
    # Description:
    # Remove comment and empty line
    def remove_comment(self):
        for line in self.asm_list:
            if '//' in line:  # remove comment
                line = line[0:line.index('//')]

            line = line.strip()  # remove white space in both left and right side

            if len(line) != 0:  # ignore empty line
                self.no_comment_list.append(line)

    def get_no_comment_list(self):
        return self.no_comment_list

    # ----------------------------------------------------------
    # Description:
    #   find and remove all Label, update the symbol_table
    def proc_label(self):
        temp_list = []
        for line in self.no_comment_list:
            if self.contain_label(line):
                cur_label = line[1:-1]
                self.symbol_table[cur_label] = str(len(temp_list))
            else:
                temp_list.append(line)
        self.no_comment_list = temp_list

    # ----------------------------------------------------------
    # Description:
    #   detect if line contain label('(' + label + ')'),
    # Input:
    #     line     one line(str) in .asm file
    @staticmethod
    def contain_label(line):
        if (line[0] == '(') and (line[-1] == ')'):
            return 1
        else:
            return 0

    # ----------------------------------------------------------
    # Description:
    #   find all variable and then add them into symbol_table, won't make change on no_comment_list
    def proc_variable(self):
        pointer_in_ram = 16
        for line in self.no_comment_list:
            if self.contain_variable(line):
                cur_variable = line[1:]
                if cur_variable not in self.symbol_table:
                    self.symbol_table[cur_variable] = str(pointer_in_ram)
                    pointer_in_ram += 1

    # ----------------------------------------------------------
    # Description:
    #   detect if line contain variable('@' is the first character and followed by a label),
    # Input:
    #     line     one line(str) in .asm file
    @staticmethod
    def contain_variable(line):
        if (line[0] == '@') and (line[1].isalpha()):
            return 1
        else:
            return 0

    # ----------------------------------------------------------
    # Description:
    #   replace all symbol encountered in .asm file with corresponding numeric value
    def replace_symbol(self):
        for line in self.no_comment_list:
            if self.contain_variable(line):  # contain variable
                cur_symbol = line[1:]
                if cur_symbol in self.symbol_table:
                    self.no_symbol_list.append('@' + self.symbol_table[cur_symbol])
                else:
                    print('[Log]:\tError_unresolved_symbol')
            else:
                self.no_symbol_list.append(line)

    def get_no_symbol_list(self):
        return self.no_symbol_list


# ----------------------------------------------------------
# Description:
#   parse .asm file into corresponding machine code file
class Parser(object):
    def __init__(self, no_symbol_list):
        self.no_symbol_list = no_symbol_list
        self.bin_list = []

        # main precess
        for line in self.no_symbol_list:
            if '@' in line:
                self.bin_list.append(self.parse_a_command(line))
            else:
                self.bin_list.append(self.parse_c_command(line))

    def get_bin_list(self):
        return self.bin_list

    # ----------------------------------------------------------
    # parse a command and then return its corresponding binary code
    # Input:
    #     command   a command line
    @staticmethod
    def parse_a_command(command):
        a_str = ''
        if command[0] == '@':
            a_str = command[1:]
        else:
            print('[Log]:\tError_failed_resolving_a_command')
            exit(0)

        bin_str = bin(int(a_str))[2:]
        while len(bin_str) < 16:
            bin_str = '0' + bin_str
        return bin_str

    # ----------------------------------------------------------
    # parse c command and then return its corresponding binary code
    # Input:
    #     command   a command line
    @staticmethod
    def parse_c_command(command):
        bin_str = '111'
        comp_dict_A = {'0': '101010',
                       '1': '111111',
                       '-1': '111010',
                       'D': '001100',
                       'A': '110000',
                       '!D': '001101',
                       '!A': '110001',
                       '-D': '001111',
                       '-A': '110011',
                       'D+1': '011111',
                       'A+1': '110111',
                       'D-1': '001110',
                       'A-1': '110010',
                       'D+A': '000010',
                       'D-A': '010011',
                       'A-D': '000111',
                       'D&A': '000000',
                       'D|A': '010101'}

        comp_dict_M = {'M': '110000',
                       '!M': '110001',
                       '-M': '110011',
                       'M+1': '110111',
                       'M-1': '110010',
                       'D+M': '000010',
                       'D-M': '010011',
                       'M-D': '000111',
                       'D&M': '000000',
                       'D|M': '010101'}

        dest_dict = {'': '000',
                     'M': '001',
                     'D': '010',
                     'MD': '011',
                     'A': '100',
                     'AM': '101',
                     'AD': '110',
                     'AMD': '111'}

        jump_dict = {'': '000',
                     'JGT': '001',
                     'JEQ': '010',
                     'JGE': '011',
                     'JLT': '100',
                     'JNE': '101',
                     'JLE': '110',
                     'JMP': '111'}

        # break command into three part
        dest = ''
        jump = ''
        if '=' in command:
            dest = command[0:command.index('=')]
            command = command[command.index('=') + 1:]

        if ';' in command:
            jump = command[command.index(';') + 1:]
            command = command[0:command.index(';')]

        comp = command

        # comp part
        if 'M' in comp:
            bin_str += '1' + comp_dict_M[comp]
        else:
            bin_str += '0' + comp_dict_A[comp]

        # dest field
        bin_str += dest_dict[dest]
        # jump field
        bin_str += jump_dict[jump]

        return bin_str


# ----------------------------------------------------------
# Description:
#       receive command parameters, validating input path, pass asm_list to assembler, write bin_list to output_path
def main():
    input_path = recv_opt_arg(sys.argv)
    print('input_path:\t' + input_path)

    if os.path.isfile(input_path):
        if input_path[-4:] == '.asm':
            output_path = input_path[0:-3] + 'hack'
            print('output_path:\t' + output_path)

            with open(input_path, 'r') as f:  # import original jack_file into a list
                asm_list = f.readlines()

            bin_list = assembler(asm_list)
            write_out_file(output_path, bin_list)
        else:
            print('[Log]:\tError_invalid_file_type')
            exit(0)
    else:
        print('[Log]:\tError_invalid_input_path')
        exit(0)


# ----------------------------------------------------------
# Description:
#       receive command line input. return input_path or print usage
# Output:
#       input_path
def recv_opt_arg(argv):
    # print('sys.argv=| ', argv, ' |')

    try:
        opts, args = getopt.gnu_getopt(argv[1:], 'i:h?', ['input_path=', 'help'])
        # 'opts' is a list of tuple ('option', 'value'), each option match one value
        # 'args' is a list contains extra arguments
        # print('opts=| ', opts, ' |')
        # print('args=| ', args, ' |')
    except getopt.GetoptError as e:
        print(e)
        print_usage(argv[0])
        sys.exit()

    input_path = os.getcwd()  # default input path
    for opt, value in opts:  # ('option', 'value'), tuple
        if opt in ['-h', '-?', '--help']:  # print help information
            print_usage(argv[0])
            exit(0)
        elif opt == '-i':  # input_path
            input_path = value

    return input_path


# ----------------------------------------------------------
# Description:
#   print usage information of this script
def print_usage(cmd):
    print(('*********************************************************\n' +
           ' --* This massage gave you some detailed information! *--\n' +
           'Usage: {0} [OPTION]... [PATH]...\n' +
           '- OPTION:\n' +
           '  {0} -i | --input_path\tinput path\n' +
           '  {0} -h | -? | --help\tprint help info and exit script\n' +
           '- PATH:\n' +
           '  Provides name of the file you want to precess or directory that contain those files\n' +
           ' --*  *-- \n' +
           '*********************************************************\n').format(cmd))


# ----------------------------------------------------------
# Description:
#       writing out_list into file named out_file_path
# Input:
#       out_file_path, out_list
def write_out_file(out_file_path, out_list):
    with open(out_file_path, 'w') as f:
        for line in out_list:
            f.write(line + '\n')


if __name__ == '__main__':
    main()
