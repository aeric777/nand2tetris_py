#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Translate .vm file into .asm file"""

__author__ = 'eric'

import getopt
import os.path
import sys


# ----------------------------------------------------------
# Remove comment and empty line
# Input:
#       f_lines   a list that contain every line of original .vm file
# ----------------------------------------------------------
def format_file(f_lines):
    res_format_file = []
    for line in f_lines:
        if '//' in line:  # remove comment
            line = line[0:line.index('//')]
        line = line.strip()  # remove backspace
        if len(line) == 0:  # ignore empty line
            continue
        else:
            res_format_file.append(line)

    return res_format_file


# ----------------------------------------------------------
# parse vm file and translate it into assembly file
# Input:
#       f_lines   a list that contain every line of original .vm file
# ----------------------------------------------------------
def parse_command(f_lines):
    re_parse_command = []

    for line in f_lines:
        c_list = line.split(' ')  # split command with backspace
        c_type = which_command(c_list)

        if c_type == 'arithmetic':
            re_parse_command = re_parse_command + c_arithmetic(c_list, label_flag)
        elif c_type == 'push':
            re_parse_command = re_parse_command + c_push(c_list)
        elif c_type == 'pop':
            re_parse_command = re_parse_command + c_pop(c_list)
        elif c_type == 'label':
            re_parse_command = re_parse_command + c_label(c_list)
        elif c_type == 'goto':
            re_parse_command = re_parse_command + c_goto(c_list)
        elif c_type == 'if':
            re_parse_command = re_parse_command + c_if(c_list)
        elif c_type == 'function':
            re_parse_command = re_parse_command + c_function(c_list)
        elif c_type == 'call':
            re_parse_command = re_parse_command + c_call(c_list, call_flag)
        elif c_type == 'return':
            re_parse_command = re_parse_command + c_return()
        else:
            print('Invalid command type!!!')
            re_parse_command = re_parse_command + ['Invalid Command Type!!!']

    return re_parse_command


# ----------------------------------------------------------
# return corresponding number of command type
# ----------------------------------------------------------
def which_command(command_list):
    arithmetic = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
    if command_list[0] in arithmetic:
        return 'arithmetic'
    elif command_list[0] == 'push':
        return 'push'
    elif command_list[0] == 'pop':
        return 'pop'
    elif command_list[0] == 'label':
        return 'label'
    elif command_list[0] == 'goto':
        return 'goto'
    elif command_list[0] == 'if-goto':
        return 'if'
    elif command_list[0] == 'function':
        return 'function'
    elif command_list[0] == 'call':
        return 'call'
    elif command_list[0] == 'return':
        return 'return'


# ----------------------------------------------------------
# parse arithmetic command
# ----------------------------------------------------------
def c_arithmetic(command_list, flag):
    command = command_list[0]
    if command == 'add':
        re_c_arithmetic = ['@SP', 'AM=M-1', 'D=M', '@SP', 'A=M-1', 'M=D+M']
    elif command == 'sub':
        re_c_arithmetic = ['@SP', 'AM=M-1', 'D=M', '@SP', 'A=M-1', 'M=M-D']
    elif command == 'neg':
        re_c_arithmetic = ['@SP', 'A=M-1', 'M=-M']
    elif command == 'eq':
        re_c_arithmetic = ['@SP', 'AM=M-1', 'D=M', '@SP', 'A=M-1', 'D=M-D', 'M=-1', '@eqTrue' + str(flag[0]), 'D;JEQ',
                           '@SP',
                           'A=M-1', 'M=0', '(eqTrue' + str(flag[0]) + ')']
        flag[0] = flag[0] + 1
    elif command == 'gt':
        re_c_arithmetic = ['@SP', 'AM=M-1', 'D=M', '@SP', 'A=M-1', 'D=M-D', 'M=-1', '@gtTrue' + str(flag[0]), 'D;JGT',
                           '@SP',
                           'A=M-1', 'M=0', '(gtTrue' + str(flag[0]) + ')']
        flag[0] = flag[0] + 1
    elif command == 'lt':
        re_c_arithmetic = ['@SP', 'AM=M-1', 'D=M', '@SP', 'A=M-1', 'D=M-D', 'M=-1', '@ltTrue' + str(flag[0]), 'D;JLT',
                           '@SP',
                           'A=M-1', 'M=0', '(ltTrue' + str(flag[0]) + ')']
        flag[0] = flag[0] + 1
    elif command == 'and':
        re_c_arithmetic = ['@SP', 'AM=M-1', 'D=M', '@SP', 'A=M-1', 'M=D&M']
    elif command == 'or':
        re_c_arithmetic = ['@SP', 'AM=M-1', 'D=M', '@SP', 'A=M-1', 'M=D|M']
    elif command == 'not':
        re_c_arithmetic = ['@SP', 'A=M-1', 'M=!M']
    else:
        re_c_arithmetic = []
        print('unknown arithmetic command!')

    return re_c_arithmetic


# ----------------------------------------------------------
# parse push command
# ----------------------------------------------------------
def c_push(command_list):
    segment = command_list[1]
    index = command_list[2]
    if segment == 'constant':
        re_c_push = ['@' + str(index), 'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    elif segment == 'static':
        re_c_push = ['@' + fileName + '.' + str(index), 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    elif segment == 'this':
        re_c_push = ['@THIS', 'D=M', '@' + str(index), 'A=D+A', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    elif segment == 'that':
        re_c_push = ['@THAT', 'D=M', '@' + str(index), 'A=D+A', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    elif segment == 'local':
        re_c_push = ['@LCL', 'D=M', '@' + str(index), 'A=D+A', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    elif segment == 'argument':
        re_c_push = ['@ARG', 'D=M', '@' + str(index), 'A=D+A', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    elif segment == 'temp':
        re_c_push = ['@5', 'D=A', '@' + str(index), 'A=D+A', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    elif segment == 'pointer':
        re_c_push = ['@3', 'D=A', '@' + str(index), 'A=D+A', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    else:
        re_c_push = []
        print('unknown arithmetic command!')
    return re_c_push


# ----------------------------------------------------------
# parse pop command
# ----------------------------------------------------------
def c_pop(command_list):
    segment = command_list[1]
    index = command_list[2]
    if segment == 'static':
        re_c_pop = ['@SP', 'AM=M-1', 'D=M', '@' + fileName + '.' + str(index), 'M=D']
    elif segment == 'this':
        re_c_pop = ['@THIS', 'D=M', '@' + str(index), 'D=D+A', '@R13', 'M=D', '@SP', 'AM=M-1', 'D=M', '@R13', 'A=M',
                    'M=D']
    elif segment == 'that':
        re_c_pop = ['@THAT', 'D=M', '@' + str(index), 'D=D+A', '@R13', 'M=D', '@SP', 'AM=M-1', 'D=M', '@R13', 'A=M',
                    'M=D']
    elif segment == 'local':
        re_c_pop = ['@LCL', 'D=M', '@' + str(index), 'D=D+A', '@R13', 'M=D', '@SP', 'AM=M-1', 'D=M', '@R13', 'A=M',
                    'M=D']
    elif segment == 'argument':
        re_c_pop = ['@ARG', 'D=M', '@' + str(index), 'D=D+A', '@R13', 'M=D', '@SP', 'AM=M-1', 'D=M', '@R13', 'A=M',
                    'M=D']
    elif segment == 'temp':
        re_c_pop = ['@5', 'D=A', '@' + str(index), 'D=D+A', '@R13', 'M=D', '@SP', 'AM=M-1', 'D=M', '@R13', 'A=M',
                    'M=D']
    elif segment == 'pointer':
        re_c_pop = ['@3', 'D=A', '@' + str(index), 'D=D+A', '@R13', 'M=D', '@SP', 'AM=M-1', 'D=M', '@R13', 'A=M',
                    'M=D']
    else:
        re_c_pop = []
        print('unknown arithmetic command!')
    return re_c_pop


# ----------------------------------------------------------
# parse label command
# ----------------------------------------------------------
def c_label(command_list):
    new_label = fileName + '$' + command_list[1]
    return ['(' + new_label + ')']


# ----------------------------------------------------------
# parse goto command
# ----------------------------------------------------------
def c_goto(command_list):
    new_label = fileName + '$' + command_list[1]
    return ['@' + new_label, '0;JMP']


# ----------------------------------------------------------
# parse if command
# ----------------------------------------------------------
def c_if(command_list):
    new_label = fileName + '$' + command_list[1]
    return ['@SP', 'AM=M-1', 'D=M', '@' + new_label, 'D;JNE']


# ----------------------------------------------------------
# parse function command
# ----------------------------------------------------------
def c_function(command_list):
    res_push = c_push(['push', 'constant', '0'])
    res = ['(' + command_list[1] + ')']
    loop_times = int(command_list[2])
    while loop_times:
        res = res + res_push
        loop_times = loop_times - 1
    return res


# ----------------------------------------------------------
# parse return command
# ----------------------------------------------------------
def c_return():
    res = ['@LCL', 'D=M', '@R13', 'M=D', '@5', 'A=D-A', 'D=M', '@R14', 'M=D', '@SP', 'AM=M-1', 'D=M', '@ARG', 'A=M',
           'M=D']
    res = res + ['@ARG', 'D=M+1', '@SP', 'M=D']
    res = res + ['@R13', 'AM=M-1', 'D=M', '@THAT', 'M=D']
    res = res + ['@R13', 'AM=M-1', 'D=M', '@THIS', 'M=D']
    res = res + ['@R13', 'AM=M-1', 'D=M', '@ARG', 'M=D']
    res = res + ['@R13', 'AM=M-1', 'D=M', '@LCL', 'M=D', '@R14', 'A=M', '0;JMP']

    return res


# ----------------------------------------------------------
# parse call command
# ----------------------------------------------------------
def c_call(command_list, call_index=None):
    if call_index is None:
        call_index = [0]

    label = command_list[1] + '.returnAddr.' + str(call_index[0])
    call_index[0] = call_index[0] + 1

    res = ['@' + label, 'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    res = res + ['@LCL', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    res = res + ['@ARG', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    res = res + ['@THIS', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    res = res + ['@THAT', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    res = res + ['@' + command_list[2], 'D=A', '@5', 'D=D+A', '@SP', 'D=M-D', '@ARG', 'M=D', '@SP', 'D=M', '@LCL',
                 'M=D', '@' + command_list[1], '0;JMP', '(' + label + ')']

    return res


# ----------------------------------------------------------
# return the Bootstrap Code
# ----------------------------------------------------------
def c_init():
    res_call = c_call(['call', 'Sys.init', '0'])
    return ['@256', 'D=A', '@SP', 'M=D'] + res_call


# ----------------------------------------------------------
# vm_translator : transfer between .vm file and assembly code
# Input:
#     fname     full path of the vm.file
# ----------------------------------------------------------
def vm_translator(fname):
    # read original vm_file line by line
    with open(fname, 'r') as f:
        vm_file = f.readlines()
    # print('Original vm_file:\tLine:', len(vm_file), '\n', vm_file)

    # remove empty-line, remove command
    vm_file = format_file(vm_file)
    # print('After format_file:\tLine:', len(vm_file), '\n', vm_file)

    asm = parse_command(vm_file)
    # print('After parse_command:\tLine:', len(asm), '\n', asm)

    return asm


# ----------------------------------------------------------
# write assembly code into .asm file
# Input:
#     fname     full path of the .asm file
#     bin_list  a list that contain all binary code
# ----------------------------------------------------------
def write_bin_file(fname, bin_list):
    with open(fname, 'w') as f:
        for line in bin_list:
            f.write(line + '\n')


def main(in_path):
    global fileName
    global label_flag
    global call_flag

    outputName = ''
    asm_file = []

    # initialize label flag
    label_flag = [0]  # 此处使用 list 是因为传递 list 到函数中，可以在函数中修改内部的数值，相当于全局变量！！！
    call_flag = [0]

    if os.path.isdir(in_path):
        # make sure that the last character of in_path is '\'
        if not (in_path[-1] == '\\'):
            in_path = in_path + '\\'

        dirs = os.listdir(in_path)
        # 如果文件夹中包含 Sys.vm 文件，则写上系统初始化命令
        if 'Sys.vm' in dirs:
            asm_file = asm_file + ['//Bootstrap Code']
            asm_file = asm_file + c_init()

        for insideDir in dirs:
            if '.vm' in insideDir:
                fullInputPath = in_path + insideDir

                fileName = insideDir[0:insideDir.rindex('.')]

                outputName = input_path + in_path.split('\\')[-2] + '.asm'

                asm_file = asm_file + ['//' + fileName]
                asm_file = asm_file + vm_translator(fullInputPath)

    elif os.path.isfile(in_path):
        fileName = in_path[in_path.rindex('\\') + 1:in_path.rindex('.')]
        outputName = in_path[:in_path.rindex('.')] + '.asm'
        asm_file = asm_file + vm_translator(in_path)

    write_bin_file(outputName, asm_file)

    return


if __name__ == '__main__':
    # print('# Current Path:', sys.argv[0])
    # print('# Current Name:', __name__)
    opts, args = getopt.gnu_getopt(sys.argv[1:], 'i:o:h', ['input_path=', 'output_path=', 'help'])
    input_path = '.'  # default input file_path
    output_path = '.'  # default output file_path
    got_input_flag = 0
    got_output_flag = 0
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
            output_path = input_path  # 给定输入文件夹之后默认输出文件夹等于输入文件夹，除非之后指定
            got_input_flag = 1
        elif '-o' == i[0]:  # output_path
            output_path = i[1]  # 指定输出文件夹
            got_output_flag = 1

    # -------------
    # main function
    main(input_path)
