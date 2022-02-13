#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description:
    compile .jack code into .vm code with 2 stages:
    .jack --> .xml
    .xml --> .vm
"""

__author__ = 'eric'

import getopt
import os.path
import sys
from JackAnalyzer import JackAnalyzer


# ----------------------------------------------------------
# Description:
#       receive source file and compile it into vm file through two stages:
#       Ⅰ.jack --> .xml     Ⅱ .xml --> .vm
# Output:
#       outputFile
# ----------------------------------------------------------
def main():
    input_path, output_path = recv_opt_arg()
    # print('input_path:\t', input_path)
    # print('output_path:\t', input_path)

    if os.path.isdir(input_path):  # is directory
        if not (input_path[-1] == '\\'):  # make sure that the last character in input_path is '\'
            input_path = input_path + '\\'
        files = os.listdir(input_path)
        for per_file in files:
            if per_file[-5:] == '.jack':  # only deal with file that end with '.jack'
                in_file_path = input_path + per_file
                file_name = per_file[0:per_file.rindex('.')]
                out_file_path = input_path + file_name + '.vm'
                # out_file_path_xml = input_path + file_name + '.xml'
                print('in_file_path\t', in_file_path)
                print('out_file_path\t', out_file_path)

                process_file(in_file_path)

    elif os.path.isfile(input_path):  # is file
        if input_path[-5:] == '.jack':  # only deal with file that end with '.jack'
            in_file_path = input_path
            out_file_path = input_path[0:-5] + '.vm'
            # out_file_path_xml = input_path[0:-5] + '.xml'
            print('in_file_path\t', in_file_path)
            print('out_file_path\t', out_file_path)

            process_file(in_file_path)
        else:
            print('!!!invalid input:\t', input_path)

    else:  # neither directory nor file
        print('!!!invalid file type, return with error.')
    return


# ----------------------------------------------------------
# Description:
#       processing file in `in_file_path` with 3 stages:
#       1.tokenize
#       2.compilation_engine
#       3.code_generation
# Input:
#       `in_file_path` that specify only one `.jack` file
# ----------------------------------------------------------
def process_file(in_file_path):
    analyzed_list = JackAnalyzer(in_file_path)
    print('analyzed_list:\n', analyzed_list)
    # write .xml file
    # write_xml_file(out_file_path_xml, analyzed_list)
    # code generation


# ----------------------------------------------------------
# Description:
#       writing analyzed_list into a .xml file named out_file_path
# Input:
#       out_file_path, analyzed_list
# ----------------------------------------------------------
def write_xml_file(out_file_path, analyzed_list):
    with open(out_file_path, 'w') as f:
        for line in analyzed_list:
            f.write(line + '\n')


# ----------------------------------------------------------
# Description:
#       receive command line input. return input_path and output_path
#       capable of print help information if '-h' option is provided
# Output:
#       input_path, output_path
# ----------------------------------------------------------
def recv_opt_arg():
    # print('# Current Path:', sys.argv[0])
    # print('# Current Name:', __name__)
    opts, args = getopt.gnu_getopt(sys.argv[1:], 'i:o:h', ['input_path=', 'output_path=', 'help'])
    input_path = '.'  # default input file_path
    output_path = '.'  # default output file_path
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
                  '$ python IOFile.py -i per_file_name\n',
                  '$ python IOFile.py -i dir_name\n',
                  '```')
        elif '-i' == i[0]:  # input_path
            input_path = i[1]
            output_path = input_path  # 给定输入文件夹之后默认输出文件夹等于输入文件夹，除非之后指定
        elif '-o' == i[0]:  # output_path
            output_path = i[1]  # 指定输出文件夹

    return input_path, output_path


if __name__ == '__main__':
    main()
