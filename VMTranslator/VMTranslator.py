#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""[two tier compile]:
Compile procedure:
    High-level language --> intermediate-code --> target machine code
Usage:
> python script.py [option] [para]
Recommend os:
    Unix-like
"""

__author__ = 'eric'

import getopt
import os.path
import sys


# ----------------------------------------------------------
# Description:
#   Translate .vm file into .asm file
def main():
    input_path = recv_opt_arg(sys.argv)
    print('input_path:\t' + input_path)

    if os.path.isdir(input_path):  # 编译文件夹中所有VM代码为一个汇编文件，输出文件和文件夹同名
        print('[Log]:\tis dir')
        input_path = os.path.abspath(input_path) + '/'  # get absolute path and make sure the last char is '/'
        output_path = input_path + input_path.split('/')[-2] + '.asm'  # 输出文件和文件夹同名

        file_path_list = []  # a list that contain every to be processed file's full path
        files = os.listdir(input_path)
        for each_file in files:  # 处理给定文件夹中的 .vm 文件
            if each_file[-3:] == '.vm':
                file_path_list.append(input_path + each_file)  # 完整路径 = 文件路径 + 文件名(带后缀)

        processing_dir_file(file_path_list, output_path)

    elif os.path.isfile(input_path):  # 编译给定文件为一个汇编文件，输出文件与编译文件同名
        print('[Log]:\tis file')
        if input_path[-3:] == '.vm':
            output_path = input_path[:-3] + '.asm'

            file_path_list = [os.path.abspath(input_path)]  # get absolute input path
            processing_dir_file(file_path_list, output_path)
        else:
            print('[Log]:\tError_invalid_file_type')
            exit(0)

    else:  # path is neither directory nor file
        print('[Log]:\tError_invalid_input_path_type')
        exit(0)

    return


# ----------------------------------------------------------
# Description:
#   processing each file in file_path_list, and write asm_list into output_path
# Input:
#   file_path_list, output_path
def processing_dir_file(file_path_list, output_path):
    print('[Log]:\t---* processing file, list:', file_path_list)
    print('[Log]:\t---* output_path:', output_path)

    asm_list = []
    for each_input_path in file_path_list:  # each_file_path is the full path of each file to be processed
        if 'Sys.vm' in each_input_path:
            print('[Log]:\tAdd Bootstrap Code')
            asm_list = ['//Bootstrap Code'] + VMTranslator.c_init() + asm_list

        with open(each_input_path, 'r') as f:  # import original jack_file into a list
            vm_list = f.readlines()
        file_name = each_input_path.split('/')[-1][0:-3]

        vm_translator = VMTranslator(vm_list, file_name)
        asm_list += vm_translator.get_asm_list()

    write_asm_file(output_path, asm_list)


# ----------------------------------------------------------
# Class Description:
# Instantiate:          VMTranslator(vm_list, file_name)
class VMTranslator(object):
    def __init__(self, vm_list, file_name):
        self.file_name = file_name
        print('[Log]:\t---* instantiate VMTranslator, file_name: ' + self.file_name)
        self.vm_list = vm_list
        # print('[Log]:\tvm_list, line:', len(self.vm_list), '\n', self.vm_list)
        self.no_comment_list = []
        self.asm_list = ['//' + self.file_name]

        self.label_flag = 0  # 多个vm文件中可能存在同名函数，标识label时在函数名前加上文件名进行标识

        # ---* main process *---
        self.format_file()  # Remove comment and empty line
        # print('[Log]:\tno_comment_list, line:', len(self.no_comment_list), '\n', self.no_comment_list)
        self.parse_command()

    def get_asm_list(self):
        return self.asm_list

    # ----------------------------------------------------------
    # Description:
    #   Remove comment and empty line
    def format_file(self):
        for line in self.vm_list:
            if '//' in line:  # remove comment
                line = line[0:line.index('//')]
            line = line.strip()  # remove backspace on both side

            if len(line) != 0:  # ignore empty line
                self.no_comment_list.append(line)

    # ----------------------------------------------------------
    # parse vm file and translate it into assembly file
    # Input:
    #       f_lines   a list that contain every line of original .vm file
    def parse_command(self):

        for line in self.no_comment_list:
            command_list = line.split(' ')  # split command with backspace
            command_type = self.which_command(command_list)

            if command_type == 'arithmetic':
                self.asm_list += self.c_arithmetic(command_list)
            elif command_type == 'push':
                self.asm_list += self.c_push(command_list)
            elif command_type == 'pop':
                self.asm_list += self.c_pop(command_list)
            elif command_type == 'label':
                self.asm_list += self.c_label(command_list)
            elif command_type == 'goto':
                self.asm_list += self.c_goto(command_list)
            elif command_type == 'if-goto':
                self.asm_list += self.c_if(command_list)
            elif command_type == 'function':
                self.asm_list += self.c_function(command_list)
            elif command_type == 'call':
                self.asm_list += self.c_call(command_list)
            elif command_type == 'return':
                self.asm_list += self.c_return()
            else:  # invalid command type
                print('[Log]:\tError_invalid_command_type')
                self.asm_list += ['Error_invalid_command_type']

    # ----------------------------------------------------------
    # return corresponding number of command type
    @staticmethod
    def which_command(command_list):
        arithmetic_command = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
        if command_list[0] in arithmetic_command:
            return 'arithmetic'
        else:  # 'arithmetic', 'push', 'pop', 'label', 'goto', 'if-goto', 'function', 'call', 'return'
            return command_list[0]

    # ----------------------------------------------------------
    # parse arithmetic command
    def c_arithmetic(self, command_list):
        command = command_list[0]
        if command == 'add':
            re_c_arithmetic = ['@SP', 'AM=M-1', 'D=M', '@SP', 'A=M-1', 'M=D+M']
        elif command == 'sub':
            re_c_arithmetic = ['@SP', 'AM=M-1', 'D=M', '@SP', 'A=M-1', 'M=M-D']
        elif command == 'neg':
            re_c_arithmetic = ['@SP', 'A=M-1', 'M=-M']
        elif command == 'eq':
            re_c_arithmetic = ['@SP', 'AM=M-1', 'D=M', '@SP', 'A=M-1', 'D=M-D', 'M=-1', '@eqTrue' + str(self.label_flag),
                               'D;JEQ',
                               '@SP',
                               'A=M-1', 'M=0', '(eqTrue' + str(self.label_flag) + ')']
            self.label_flag += 1
        elif command == 'gt':
            re_c_arithmetic = ['@SP', 'AM=M-1', 'D=M', '@SP', 'A=M-1', 'D=M-D', 'M=-1', '@gtTrue' + str(self.label_flag),
                               'D;JGT',
                               '@SP',
                               'A=M-1', 'M=0', '(gtTrue' + str(self.label_flag) + ')']
            self.label_flag += 1
        elif command == 'lt':
            re_c_arithmetic = ['@SP', 'AM=M-1', 'D=M', '@SP', 'A=M-1', 'D=M-D', 'M=-1', '@ltTrue' + str(self.label_flag),
                               'D;JLT',
                               '@SP',
                               'A=M-1', 'M=0', '(ltTrue' + str(self.label_flag) + ')']
            self.label_flag += 1
        elif command == 'and':
            re_c_arithmetic = ['@SP', 'AM=M-1', 'D=M', '@SP', 'A=M-1', 'M=D&M']
        elif command == 'or':
            re_c_arithmetic = ['@SP', 'AM=M-1', 'D=M', '@SP', 'A=M-1', 'M=D|M']
        elif command == 'not':
            re_c_arithmetic = ['@SP', 'A=M-1', 'M=!M']
        else:
            re_c_arithmetic = []
            print('[Log]:\tError_unknown_arithmetic_command')
            exit(0)

        return re_c_arithmetic

    # ----------------------------------------------------------
    # parse push command
    def c_push(self, command_list):
        segment = command_list[1]
        index = command_list[2]
        if segment == 'constant':
            re_c_push = ['@' + str(index), 'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        elif segment == 'static':
            re_c_push = ['@' + self.file_name + '.' + str(index), 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
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
    def c_pop(self, command_list):
        segment = command_list[1]
        index = command_list[2]
        if segment == 'static':
            re_c_pop = ['@SP', 'AM=M-1', 'D=M', '@' + self.file_name + '.' + str(index), 'M=D']
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
    def c_label(self, command_list):
        new_label = self.file_name + '$' + command_list[1]  # mark different labels
        return ['(' + new_label + ')']

    # ----------------------------------------------------------
    # parse goto command
    def c_goto(self, command_list):
        new_label = self.file_name + '$' + command_list[1]
        return ['@' + new_label, '0;JMP']

    # ----------------------------------------------------------
    # parse if command
    def c_if(self, command_list):
        new_label = self.file_name + '$' + command_list[1]
        return ['@SP', 'AM=M-1', 'D=M', '@' + new_label, 'D;JNE']

    # ----------------------------------------------------------
    # parse function command
    def c_function(self, command_list):
        res_push = self.c_push(['push', 'constant', '0'])
        res = ['(' + command_list[1] + ')']
        loop_times = int(command_list[2])
        while loop_times:
            res = res + res_push
            loop_times = loop_times - 1
        return res

    # ----------------------------------------------------------
    # parse return command
    # ----------------------------------------------------------
    @staticmethod
    def c_return():
        res = ['@LCL', 'D=M', '@R13', 'M=D', '@5', 'A=D-A', 'D=M', '@R14', 'M=D', '@SP', 'AM=M-1', 'D=M', '@ARG', 'A=M',
               'M=D']
        res += ['@ARG', 'D=M+1', '@SP', 'M=D']
        res += ['@R13', 'AM=M-1', 'D=M', '@THAT', 'M=D']
        res += ['@R13', 'AM=M-1', 'D=M', '@THIS', 'M=D']
        res += ['@R13', 'AM=M-1', 'D=M', '@ARG', 'M=D']
        res += ['@R13', 'AM=M-1', 'D=M', '@LCL', 'M=D', '@R14', 'A=M', '0;JMP']

        return res

    # ----------------------------------------------------------
    # parse call command
    @staticmethod
    def c_call(command_list):
        global CALL_FLAG
        label = command_list[1] + '.returnAddr.' + str(CALL_FLAG)
        # 此处call_flag设立是为了防止同一个vm文件中多次调用同一函数，导致出现多个相同label
        # 但是对于每个文件单独维护的call_flag，到处理另一个文件时由于新建VMTranslator对象会导致该变量重置为0
        # 以至于无法处理多个文件多次调用同名函数的bug
        # 可选解决方案：
        #   1. 将call_flag的维护调整为全局，也即是对于所有文件公共维护同一个CALL_FLAG (yes)
        #   2. 通过if语句手动排除 (no)
        CALL_FLAG += 1

        res = ['@' + label, 'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        res += ['@LCL', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        res += ['@ARG', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        res += ['@THIS', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        res += ['@THAT', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        res += ['@' + command_list[2], 'D=A', '@5', 'D=D+A', '@SP', 'D=M-D', '@ARG', 'M=D', '@SP', 'D=M', '@LCL',
                'M=D', '@' + command_list[1], '0;JMP', '(' + label + ')']
        return res

    # ----------------------------------------------------------
    # Description:
    #   return the Bootstrap Code
    @staticmethod
    def c_init():
        res_init = ['@256', 'D=A', '@SP', 'M=D']
        res_call = VMTranslator.c_call(['call', 'Sys.init', '0'])

        return res_init + res_call  # 将寄存器SP置为256 + 调用函数Sys.init


# ----------------------------------------------------------
# Description:
#   write assembly code to .asm file
# Input:
#   out_file_path, asm_list
def write_asm_file(out_file_path, asm_list):
    with open(out_file_path, 'w') as f:
        for line in asm_list:
            f.write(line + '\n')


# ----------------------------------------------------------
# Description:
#   receive command line input. return input_path or print usage
# Output:
#   input_path
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


if __name__ == '__main__':
    CALL_FLAG = 0  # 一个文件中可能存在多次调用同一函数的情况，调用代码结尾的label需要加上flag标识
    main()
