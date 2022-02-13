#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""No description"""

__author__ = 'eric'

import getopt
import sys


# ----------------------------------------------------------
# parse asm.file into corresponding binary file
# Input:
#     fname   full path of the file you wanna parse
# ----------------------------------------------------------
def parser(f_lines):
    res_parser = []
    for line in f_lines:
        if '@' in line:  # processing a_command
            res_parser.append(parse_a_command(line))
        else:  # processing c_command
            res_parser.append(parse_c_command(line))

    return res_parser


# ----------------------------------------------------------
# parse a command and then return its corresponding binary code
# Input:
#     command   a command line
# ----------------------------------------------------------
def parse_a_command(command):
    if command[0] == '@':
        a_str = command[1:]
    else:
        print('bad command!')
        return -1

    bin_str = bin(int(a_str))[2:]
    while len(bin_str) < 16:
        bin_str = '0' + bin_str
    return bin_str


# ----------------------------------------------------------
# parse c command and then return its corresponding binary code
# Input:
#     command   a command line
# ----------------------------------------------------------
def parse_c_command(command):
    bin_str = '111'
    comp_dict_A = {
        '0': '101010',
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
        'D|A': '010101'
    }

    comp_dict_M = {
        'M': '110000',
        '!M': '110001',
        '-M': '110011',
        'M+1': '110111',
        'M-1': '110010',
        'D+M': '000010',
        'D-M': '010011',
        'M-D': '000111',
        'D&M': '000000',
        'D|M': '010101'
    }

    dest_dict = {
        '': '000',
        'M': '001',
        'D': '010',
        'MD': '011',
        'A': '100',
        'AM': '101',
        'AD': '110',
        'AMD': '111'
    }

    jump_dict = {
        '': '000',
        'JGT': '001',
        'JEQ': '010',
        'JGE': '011',
        'JLT': '100',
        'JNE': '101',
        'JLE': '110',
        'JMP': '111'
    }

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

    # dest part
    bin_str += dest_dict[dest]
    # jump part
    bin_str += jump_dict[jump]

    return bin_str


# ----------------------------------------------------------
# Remove comment and empty line
# Input:
#       f_lines   a list that contain every line of original asm.file
# ----------------------------------------------------------
def format_file(f_lines):
    res_format_file = []
    for line in f_lines:
        if '//' in line:  # remove comment
            line = line[0:line.index('//')]
        line = line.strip()  # remove backspace
        if len(line) == 0:  # ignore empty line
            continue
        res_format_file.append(line)

    return res_format_file


# ----------------------------------------------------------
# Find all Label and then add them to 'symbol table'
# Input:
#       f_lines   a list that contain every line of original asm.file
#       symbol    'symbol table' - symbol
#       value     'symbol table' - value
# ----------------------------------------------------------
def find_label(f_lines, symbol, value):
    res_find_label = []
    for line in f_lines:
        if ('(' in line) and (')' in line):
            curLabel = line.replace('(', '').replace(')', '')
            symbol.append(curLabel)
            value.append(str(len(res_find_label)))
        else:
            res_find_label.append(line)

    return res_find_label


# ----------------------------------------------------------
# assembler : transfer between assembly language and machine language(binary code)
# Input:
#     fname     full path of the asm.file
# ----------------------------------------------------------
def assembler(fname):
    # built 'symbol table'
    symbol_name = ['SP',
                   'LCL',
                   'ARG',
                   'THIS',
                   'THAT',
                   'R0',
                   'R1',
                   'R2',
                   'R3',
                   'R4',
                   'R5',
                   'R6',
                   'R7',
                   'R8',
                   'R9',
                   'R10',
                   'R11',
                   'R12',
                   'R13',
                   'R14',
                   'R15',
                   'SCREEN',
                   'KBD']  # builtin symbol
    co_value = ['0',
                '1',
                '2',
                '3',
                '4',
                '0',
                '1',
                '2',
                '3',
                '4',
                '5',
                '6',
                '7',
                '8',
                '9',
                '10',
                '11',
                '12',
                '13',
                '14',
                '15',
                '16384',
                '24576'
                ]

    with open(fname, 'r') as f:
        asm_file = f.readlines()

    # remove empty-line, remove command
    asm_file = format_file(asm_file)
    print('after format_file:\t', asm_file)
    # add label into 'symbol table'
    asm_file = find_label(asm_file, symbol_name, co_value)
    print('after find_label:\t', asm_file)

    # first pass:   built full symbol table(symbol_name and co_value)
    pass_fir(asm_file, symbol_name, co_value)

    # second pass:   replace all symbol encountered with corresponding value
    asm_file = pass_sec(asm_file, symbol_name, co_value)
    print('after pass_sec:\t\t', asm_file)

    res_assembler = parser(asm_file)  # return a list that contain binary code corresponding to the asm.file
    print('after parser:\t\t', res_assembler)

    return res_assembler


# ----------------------------------------------------------
# first pass in processing asm file:
#       build full 'Symbol Table', which contain builtin symbol and new variables an new label
# Input:
#     fname     full path of the asm.file
#     symbol    symbol table
#     value    symbol table
# ----------------------------------------------------------
def pass_fir(f_lines, symbol, value):
    pointer_in_ram = 16
    for line in f_lines:
        if contain_symbol(line):
            cur_symbol = line[1:]
            if not (cur_symbol in symbol):
                symbol.append(cur_symbol)
                value.append(str(pointer_in_ram))
                pointer_in_ram = pointer_in_ram + 1


# ----------------------------------------------------------
# second pass in processing asm file:
#       replace all symbol encountered with corresponding value
# Input:
#     fname     full path of the asm.file
#     symbol    symbol table
#     value    symbol table
# ----------------------------------------------------------
def pass_sec(f_lines, symbol, value):
    for line in f_lines:
        if contain_symbol(line):
            cur_symbol = line[1:]
            if cur_symbol in symbol:
                f_lines[f_lines.index(line)] = '@' + value[symbol.index(cur_symbol)]
            else:
                print('failed due to unexpected symbol')
    return f_lines


# ----------------------------------------------------------
# detect if line contain symbol(with '@' as the first character but what follows it is not a number),
# return 1 if it does
# Input:
#     line     specific line in asm.file
# ----------------------------------------------------------
def contain_symbol(line):
    if line[0] != '@':
        return 0
    for char in line[1:]:
        if (char < '0') or (char > '9'):
            return 1
    return 0


# ----------------------------------------------------------
# write binary code into hack.file
# Input:
#     fname     full path of the hack.file
#     bin_list  a list that contain all binary code
# ----------------------------------------------------------
def write_bin_file(fname, bin_list):
    with open(fname, 'w') as f:
        for line in bin_list:
            f.write(line + '\n')


if __name__ == '__main__':
    print('# Current Path:', sys.argv[0])
    print('# Current Name:', __name__)

    # normally this argument is given from command line
    input_path = r'D:\Users\Class\nand2tetris\projects\06\\'  # default in current file
    output_path = input_path  # default in current file

    opts, args = getopt.gnu_getopt(sys.argv[1:], 'i:o:h',
                                   ['input_path=', 'output_path=', 'help'])  # v为一个开关选项，f和d表示后面要添加参数
    for i in opts:
        if '-h' == i[0]:  # print help information
            print(' --* This massage gave you some detailed information! *--\n',
                  'Usage: python [script_name].py [OPTION]... [PATH]...\n',
                  '- OPTION:\n', '	Provided options',
                  '	-i	input path\n',
                  '	-o	output path\n',
                  '	-h	print help information\n',
                  '- PATH:\n',
                  '	 Provides name of the file you want to precess '
                  'or directory that contain the files you want to process\n',
                  '- EXAMPLE:\n',
                  '```\n',
                  '$ python IOFile.py -i file_name\n',
                  '$ python IOFile.py -i dir_name\n',
                  '```')
        elif '-i' == i[0]:  # input_path
            input_path = i[1]
        elif '-o' == i[0]:  # output_path
            output_path = i[1]
    fileName = args[0]
    hack_file = assembler(input_path + fileName)
    write_bin_file(output_path + fileName[0:fileName.index('.') + 1] + 'hack', hack_file)
