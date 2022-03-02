#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description:
    compile .jack code into .vm code with 2 stages:
    .jack --> .xml
    .xml --> .vm
Recommended OS: Linux
"""

__author__ = 'eric'

import getopt
import os
import sys
from JackAnalyzer import syntax_analyzer


# ----------------------------------------------------------
# Description:
#   receive command parameters, validating input path, process each .jack file
def main():
    PROC_MODE = '.xml'  # 'T.xml' | '.xml' | '.vm'
    input_path = recv_opt_arg(sys.argv)
    # print('input_path:\t' + input_path)

    if os.path.isdir(input_path):  # path is a directory
        # print('[Log]:\tis dir')
        input_path = os.path.abspath(input_path) + '/'
        # if input_path[-1] != '/':  # make sure that the last character in input_path is '/'
        #     input_path = input_path + '/'

        files = os.listdir(input_path)
        for each_file in files:
            if each_file[-5:] == '.jack':  # only deal with file that end with '.jack'
                in_file_path = input_path + each_file  # file path that end with .jack
                out_file_path = input_path + each_file[0:-5]  # in_file_path remove .jack
                print('in_file_path\t', in_file_path)
                print('out_file_path\t', out_file_path)

                process_file(in_file_path, out_file_path, PROC_MODE)

    elif os.path.isfile(input_path):  # path is a file
        # print('[Log]:\tis file')
        input_path = os.path.abspath(input_path)
        if input_path[-5:] == '.jack':  # only deal with file that end with '.jack'
            in_file_path = input_path  # file path that end with .jack
            out_file_path = input_path[0:-5]  # in_file_path remove .jack
            print('in_file_path\t', in_file_path)
            print('out_file_path\t', out_file_path)

            process_file(in_file_path, out_file_path, PROC_MODE)
        else:
            print('[Error]:\tinvalid file type(should be .jack file): ' + input_path)

    else:  # path is neither directory nor file
        print('[Error]:\tgiven path is neither directory nor file, return with error.')

    return


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
#       Main function for compiling .jack code into .vm code, two stages
#       1.code_analyzer:
#           (1) tokenize
#           (2) compilation_engine
#       2.code_generation
# Input:
#       in_file_path, out_file_path, out_mode
def process_file(in_file_path, out_file_path, out_mode):
    print('[Log]:\t--* JackCompiler, in_file_path: ' + in_file_path + ' *--')

    with open(in_file_path, 'r') as f:  # import original jack_file into a list
        jack_list = f.readlines()

    # 1.code_analyzer
    analyzed_list = syntax_analyzer(jack_list, out_mode)  # list of str, each element is one line of (T.xml|.xml) file
    print('[Log]:\tAnalyzer:\tDone')
    print('[Log]:\tOutput mode:\t' + out_mode)
    print('[Log]:\tLength:\t\t' + str(len(analyzed_list)))

    # 2.code_generation TODO
    # list of str, each element is one line of .vm file

    # write output file
    if (out_mode == 'T.xml') or (out_mode == '.xml'):
        write_out_file(out_file_path + out_mode, analyzed_list)
    # elif out_mode == '.vm':
    #     write_out_file(out_file_path + out_mode, vm_list)


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
