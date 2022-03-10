#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description:
    compile .jack code into .vm code with 2 stages:
    .jack --> .xml
    .xml --> .vm
Recommended OS:
    Linux
"""

__author__ = 'eric'

import getopt
import os
import sys
from Analyzer import syntax_analyzer
from Code_generation import CompilationEngineToVM


# ----------------------------------------------------------
# Description:
#   receive command parameters --> validating input path --> processing each .jack file
def main():
    input_path, PROC_MODE = recv_opt_arg(sys.argv)

    if os.path.isdir(input_path):  # path is a directory
        input_path = os.path.abspath(input_path) + '/'  # make sure that the last character in input_path is '/'

        files = os.listdir(input_path)
        for each_file in files:
            if each_file[-5:] == '.jack':  # only deal with file that end with '.jack'
                no_postfix_path = input_path + each_file[0:-5]  # full path of .jack file without .jack postfix
                # print('in_file_path\t', no_postfix_path + '.jack')
                # print('out_file_path\t', no_postfix_path + PROC_MODE)

                process_file(no_postfix_path + '.jack', no_postfix_path, PROC_MODE)

    elif os.path.isfile(input_path):  # path is a file
        input_path = os.path.abspath(input_path)
        if input_path[-5:] == '.jack':  # only deal with file that end with '.jack'
            no_postfix_path = input_path[0:-5]
            # print('in_file_path\t', input_path)
            # print('out_file_path\t', no_postfix_path + PROC_MODE)

            process_file(input_path, no_postfix_path, PROC_MODE)
        else:
            print('[Error]:\tError_invalid_input_path: ' + input_path)
            exit(0)

    else:  # path is neither directory nor file
        print('[Error]:\tError_invalid_input_path: ' + input_path)
        exit(0)

    return


# ----------------------------------------------------------
# Description:
#       receive command line input. return input_path or print usage
# Output:
#       input_path, proc_mode
def recv_opt_arg(argv):
    # print('sys.argv=| ', argv, ' |')
    try:
        opts, args = getopt.gnu_getopt(argv[1:], 'i:m:h?', ['input_path=', 'proc_mode=', 'help'])
        # 'opts' is a list of tuple ('option', 'value'), each option can only be given one value
        # 'args' is a list of string containing extra arguments that are not included in list opts
        # print('opts=| ', opts, ' |')
        # print('args=| ', args, ' |')
    except getopt.GetoptError as e:  # error control
        print(e)
        print_usage(argv[0])
        sys.exit()

    input_path = ''  # default input_path is none
    proc_mode = '.vm'  # default processing mode
    for opt, value in opts:  # ('option', 'value'), tuple
        if opt in ['-h', '-?', '--help']:  # print help information
            print_usage(argv[0])
            exit(0)
        elif opt in ['-i', '--input_path']:  # input_path
            input_path = value
        elif opt in ['-m', '--proc_mode']:
            if value == 'Txml':
                proc_mode = 'T.xml'
            elif value == 'xml':
                proc_mode = '.xml'
            elif value == 'vm':
                proc_mode = '.vm'
            else:
                print('[Log]:\tError_invalid_processing_mode: ' + value)
                print_usage(argv[0])
                exit(0)

    if input_path == '':  # if no input_path is specified, print usage
        print('[Log]:\tError_no_input_path')
        print_usage(argv[0])
        exit(0)

    return input_path, proc_mode


# ----------------------------------------------------------
# Description:
#   print usage information of this script
def print_usage(cmd):
    print(('*********************************************************\n' +
           ' --* This massage gave you some detailed information! *--\n' +
           'Usage: {0} [OPTION]... [PATH]...\n' +
           '- OPTION:\n' +
           '  {0} -i | --input_path\tinput path, if not specified, print usage\n' +
           '  {0} -m | --proc_mode\tspecify the process mode(default in .vm mode)\n' +
           '- Acceptable proc_mode:\t\t\tTxml | xml | vm\n' +
           '  {0} -h | -? | --help\tprint help info and exit script\n' +
           '- PATH:\n' +
           '  Provides name of the file you want to precess or directory that contain those files\n' +
           ' --*  *-- \n' +
           '*********************************************************\n').format(cmd))


# ----------------------------------------------------------
# Description:
#       Main function for compiling .jack code into .vm code, two stages
#       1.code_analyzer:
#           (1) tokenize
#           (2) compilation_engine
#       2.code_generation
#           (1) CompilationEngineToVM
#           (2) SymbolTable
#           (3) VMWriter
# Input:
#       in_file_path, out_file_path, out_mode
def process_file(in_file_path, no_postfix_path, out_mode):
    print('[Log]:\t--* JackCompiler:\t' + in_file_path)
    print('[Log]:\t--* Processing mode:\t' + out_mode)

    with open(in_file_path, 'r') as f:  # import original jack_file into a list
        jack_list = f.readlines()

    # 1.code_analyzer
    # list of str, each element is one line of (T.xml|.xml) file
    # if out_mode is .vm, then return only tokenized_list
    analyzed_list = syntax_analyzer(jack_list, out_mode)

    # write output file
    if out_mode in ['T.xml', '.xml']:
        write_out_file(no_postfix_path + out_mode, analyzed_list)
        print('[Log]:\tanalyzed_list, Length:\t\t' + str(len(analyzed_list)))
    elif out_mode == '.vm':
        # 2.code_generation
        # receive analyzed_list and generate .vm code
        compilation_engine_to_vm = CompilationEngineToVM(analyzed_list)
        vm_list = compilation_engine_to_vm.get_vm_list()  # list of str, each element is one line of .vm file
        print('[Log]:\tvm_list, Length:\t\t' + str(len(vm_list)))
        write_out_file(no_postfix_path + out_mode, vm_list)


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
