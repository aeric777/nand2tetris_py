#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Translate .vm file into .asm file"""

__author__ = 'eric'

import re


# ----------------------------------------------------------
# Description:
#       return all start index of sub_string in main_string
# Output:
#       main_string sub_string
# Caution:
#       this function use Regex to processing string, be sure your sub_string is a valid Regex
# ----------------------------------------------------------
def index_all(main_str, sub_str):
    return [each.start() for each in re.finditer(sub_str, main_str)]


# ----------------------------------------------------------
# Description:
#       return all end index of sub_string in main_string
# Output:
#       main_string sub_string
# Caution:
#       this function use Regex to processing string, be sure your sub_string is a valid Regex
# ----------------------------------------------------------
def index_all_end(main_str, sub_str):
    starts = index_all(main_str, sub_str)
    return [start + len(sub_str) - 1 for start in starts]


def write_xml_file(out_file_path, analyzed_list):
    with open(out_file_path, 'w') as f:
        for line in analyzed_list:
            f.write(line + '\n')


# ----------------------------------------------------------
# Description:
#       receive source file and compile it into vm file through two stages:
#       Ⅰ.jack --> .xml     Ⅱ .xml --> .vm
# Output:
#       analyzed_list
# ----------------------------------------------------------
def JackAnalyzer(in_file_path):
    print('---* JackAnalyzer *---')
    print('in_file_path:\t', in_file_path)

    # import original jack_file into a list that contain every line of jack_file
    with open(in_file_path, 'r') as f:
        jack_list = f.readlines()
    print('Original jack_file:\tLine:', len(jack_list), '\n', jack_list)

    tokenized_list = JackTokenizer(jack_list)
    print('tokenized jack_file:\tLine:', len(tokenized_list), '\n', tokenized_list)


# ----------------------------------------------------------
# Description:
#       tokenize input jack_list, remove white space and comments
#       separate each token and marked it up with xml tags
# Input:
#       jack_list
# Output:
#       tokenized_list
# ----------------------------------------------------------
def JackTokenizer(jack_list):
    tokenized_list = []
    # remove white space at left and right side, remove comments
    no_comment_list = remove_comment(jack_list)
    print('remove comments:\tLine:', len(no_comment_list), '\n', no_comment_list)
    # split with white space and symbols
    token_list = split_token(no_comment_list)
    # write_xml_file('./token_list.txt', token_list)
    print('split token:\tLine:', len(token_list), '\n', token_list)

    return tokenized_list


# using regular expression
# ----------------------------------------------------------
# Description:
#       remove white space and comments
# Input:
#       jack_list
# Output:
#       no_comment_list
# ----------------------------------------------------------
def remove_comment(jack_list):
    no_comment_list = []
    multi_l_comm_status = 0
    for line in jack_list:
        line = line.strip()

        # being in multi line comment
        if multi_l_comm_status:
            if line[-2:] == r'*/':
                multi_l_comm_status = 0
            continue
        # empty line
        elif len(line) == 0:
            continue
        # single line comment
        elif (line[0:2] == r'//') or ((line[0:2] == r'/*') and (line[-2:] == r'*/')):
            continue
        # start a multi line comment
        elif line[0:3] == r'/**':
            multi_l_comm_status = 1
            continue
        # in line comment
        elif r'//' in line:
            line = proc_in_line_comm(line, '//')
        elif r'/*' in line:
            line = proc_in_line_comm(line, '/\*')

        no_comment_list.append(line)

    return no_comment_list


# ----------------------------------------------------------
# Description:
#       processing and eliminate in-line comment, 可能同时存在字符串和注释，重点处理注释符号出现在字符串中间的情况
# Input:
#       line, symbol
# Output:
#       line without comment
# ----------------------------------------------------------
def proc_in_line_comm(line, symbol):
    if '\"' in line:
        symbol_index = index_all(line, symbol)
        for per_index in symbol_index:
            if (line.count('\"', 0, per_index) % 2) == 0:
                line = line[0:per_index]
    else:
        line = line[0:line.index(symbol)]
    return line


# ----------------------------------------------------------
# Description:
#       split every token and form a list
# Input:
#       no_comment_list
# Output:
#       token_list
# ----------------------------------------------------------
def split_token(no_comment_list):
    token_list = []
    for line in no_comment_list:
        line = line.strip()
        if '\"' in line:
            print("!!!Processing:", line)
            split_quote = line.split('\"')
            print('split_quote', split_quote)
            num_flag = 0
            token_per_line = []
            for each_split in split_quote:
                if num_flag % 2 == 0:
                    num_flag = num_flag + 1
                else:
                    token_per_line.append(each_split)
                    num_flag = num_flag + 1
        else:
            split_list = line.split(' ')
            for split_list_item in split_list:
                token_list.append(split_list_item)

    return token_list


def CompilationEngine():
    pass


if __name__ == '__main__':
    print('!!!Warning:\n',
          '\tthis script can\'t be used in this way\n',
          '\tplease user JackCompiler.py instead')
