#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Translate .vm file into .asm file"""

__author__ = 'eric'

import re


# ----------------------------------------------------------
# Description:  receive jack list(list of str-line of .jack code)
#                   (1) remove comments & tokenize jack code  -  JackTokenizer(class)
#                   (2) parse jack code according to .jack grammar  -  CompilationEngine(class)
# Input:        jack_list, out_mode
# Output:       analyzed_list ('T.xml' or '.xml' mode)
def syntax_analyzer(jack_list, out_mode):
    analyzed_list = []

    jack_tokenizer = JackTokenizer(jack_list)  # instantiate JackTokenizer with parameter jack_list
    # no_comment_list = jack_tokenizer.get_no_comment_list()
    # print('remove comments:\tLine:', len(no_comment_list), '\n', no_comment_list)
    tokenized_list = jack_tokenizer.get_tokenized_list()
    # print('tokenized jack_file:\tLine:', len(tokenized_list), '\n', tokenized_list)

    compile_engine = CompilationEngine(tokenized_list)  # instantiate CompilationEngine with parameter tokenized_list
    parsed_list = compile_engine.get_parsed_list()  # parsed_list is list of str, each str is a line of final xml file
    # print('parsed list:\tLine:', len(parsed_list), '\n', parsed_list)
    # parsed_list = []

    if out_mode == 'T.xml':  # build list of 'T.xml' mode .xml file
        analyzed_list.append('<tokens>')
        for each_token in tokenized_list:
            if each_token[0] == '<':
                analyzed_list.append('<symbol> &lt; </symbol>')
            elif each_token[0] == '>':
                analyzed_list.append('<symbol> &gt; </symbol>')
            elif each_token[0] == '&':
                analyzed_list.append('<symbol> &amp; </symbol>')
            else:
                analyzed_list.append('<' + each_token[1] + '> ' + each_token[0] + ' </' + each_token[1] + '>')
        analyzed_list.append('</tokens>')
    elif out_mode == '.xml':
        # fixed display bug('<' '>' '&') in xml format
        num_flag = 0
        for each_str in parsed_list:
            if ' < ' in each_str:
                parsed_list[num_flag] = parsed_list[num_flag].replace(' < ', ' &lt; ')
            elif ' > ' in each_str:
                parsed_list[num_flag] = parsed_list[num_flag].replace(' > ', ' &gt; ')
            elif ' & ' in each_str:
                parsed_list[num_flag] = parsed_list[num_flag].replace(' & ', ' &amp; ')
            num_flag = num_flag + 1
        analyzed_list = analyzed_list + parsed_list

    return analyzed_list


# ----------------------------------------------------------
# Class Description:
# Instantiate:          JackTokenizer(jack_list)
class JackTokenizer(object):
    def __init__(self, jack_list):
        self.jack_list = jack_list
        self.no_comment_list = []  # list of str, each element is a line of .jack code
        self.tokenized_list = []  # tokenized_list is a list of tuple[('token', 'token_type')]

        # main tokenizer process
        self.remove_comment()  # 第一种类内函数调用方法：使用self实例自带的方法
        self.jack_tokenizer()

    def get_no_comment_list(self):
        return self.no_comment_list

    def get_tokenized_list(self):
        return self.tokenized_list

    # ----------------------------------------------------------
    # Description:  remove white space and comments
    # Input:        jack_list
    # Output:       no_comment_list
    def remove_comment(self):
        multi_l_comm_status = 0
        for line in self.jack_list:
            line = line.strip()  # remove white space in both left and right side

            if multi_l_comm_status:  # being in multi-line comment
                if line[-2:] == '*/':
                    multi_l_comm_status = 0
                continue
            elif len(line) == 0:  # empty line
                continue
            elif (line[0:2] == '//') or ((line[0:2] == '/*') and (line[-2:] == '*/')):  # single line comment
                continue
            elif line[0:3] == '/**':  # start a multi line comment
                multi_l_comm_status = 1
                continue
            elif '//' in line:  # in line comment
                line = self.proc_inline_comm(line, r'//')
            elif '/*' in line:  # in line comment
                line = self.proc_inline_comm(line, r'/\*')  # r'/\*'作为regex使用，必须使用'\*'转义字符

            line = line.strip()  # remove white space in both left and right side
            self.no_comment_list.append(line)

    # ----------------------------------------------------------
    # Description:  processing and eliminate in-line comment, 可能同时存在字符串和注释，重点处理注释符号出现在字符串中间的情况
    # Input:        line(str), symbol
    # Output:       line without comment(str)
    # 当我们需要某些功能而不是对象，而需要完整的类时，我们可以使方法静态化，它们通常与对象生命周期无关
    @staticmethod  # 声明静态方法，不需要传递self变量。
    def proc_inline_comm(line, symbol):
        if '"' in line:  # 该行包含str，需判断注释部分是否属于str内容
            symbol_index = index_all(line, symbol)  # get all index of symbol in line
            for per_index in symbol_index:  # 从第一个symbol开始，如果该symbol左边有偶数个引号，代表有完整的str，该symbol为注释
                if (line.count('"', 0, per_index) % 2) == 0:  # str.count(sub, start= 0,end=len(string))
                    line = line[0:per_index]
        else:  # 不含str，直接找到第一个注释符号，移除后面的内容
            line = line[0:line.index(symbol)]

        return line

    # ----------------------------------------------------------
    # Description:  tokenize input jack_list, separate each token and marked it up, compose a tuple[('token', 'token_type')]
    # Input:        no_comment_list
    # Output:       tokenized_list
    def jack_tokenizer(self):
        for line in self.no_comment_list:  # line is a string
            if '"' in line:  # .jack code contains str, separate with white_space firstly
                split_with_quote = line.split('"')  # split with "，double quote

                # str中的字符串应当作为一个整体加入token_list，不能简单用空格分开
                num_flag = False
                for each_split in split_with_quote:
                    if not num_flag:
                        self.tokenized_list = self.tokenized_list + self.split_str(each_split)
                    else:  # string constant
                        self.tokenized_list.append((each_split, 'stringConstant'))
                    num_flag = not num_flag

            else:  # line中不含str，直接进行分隔程序
                self.tokenized_list = self.tokenized_list + self.split_str(line)

    # ----------------------------------------------------------
    # Description:  split one str of jack code into tokens and marked it up, compose a tuple[('token', 'token_type')]
    # Input:        line(string)
    # Output:       split_token_list, each element is a tuple[('token', 'token_type')]
    def split_str(self, line):
        split_list = []
        keyword_jack = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char',
                        'boolean',
                        'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
        symbol_jack = ['++', '<=', '>=', '==', '{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/',
                       '&', '|', '<', '>', '=', '~']  # 注意顺序(例：'++'应该在'+'前面)

        split_with_space = line.split(' ')
        for each in split_with_space:  # each is a string with no white space inside
            # print('[Log]:\tProcessing each = ' + each)
            if len(each) == 0:
                continue
            elif each.isalpha():  # alpha
                if each in keyword_jack:  # alpha --> keyword
                    split_list.append((each, 'keyword'))
                else:  # alpha --> identifier
                    split_list.append((each, 'identifier'))
            elif each.isdigit():  # digit
                split_list.append((each, 'integerConstant'))
            elif each.isalnum():  # mixed alpha and digit
                if each[0].isdigit():
                    print('[Warning]:\tidentifier can\'t starts with digit\n' +
                          '[Processing End]')
                    exit(0)
                else:
                    split_list.append((each, 'identifier'))
            elif each in symbol_jack:  # symbol_single
                split_list.append((each, 'symbol'))
            else:  # mixed alpha and digit and symbol
                # print('[Log]:\tmixed,each = ' + each)
                found_flag = False
                for symbol in symbol_jack:
                    if symbol in each:
                        found_flag = True
                        split_list = split_list + self.split_str(each[0:each.index(symbol)]) + [
                            (symbol, 'symbol')] + self.split_str(each[each.index(symbol) + len(symbol):])
                        # 可以采用第二种类内函数调用方法：JackTokenizer.split_str()
                        # 若将本函数写作静态函数，即没有self实例，即可采用该方法
                        break  # 当一个str中存在多个symbol时，会处理多遍，导致重复，应退出循环

                if not found_flag:
                    print('[Unfixed]:\t' + each)

        return split_list


# ----------------------------------------------------------
# Class Description:
# Instantiate:          CompilationEngine(tokens_list)
class CompilationEngine(object):
    def __init__(self, tokens_list):
        self.tokens_list = tokens_list.copy()  # tokenized_list is a list of tuple[('token', 'token_type')]
        self.parsed_list = []  # parsed_list is list of str, each str is a line of final xml file

        # main compilation engine process
        self.compile_class()
        if len(self.tokens_list) != 0:
            print('[Log]:\tError_unparsered_token:', self.tokens_list)

    def get_parsed_list(self):
        return self.parsed_list

    def head_str(self):
        return self.tokens_list[0][0]

    def head_type(self):
        return self.tokens_list[0][1]

    def head_pop(self):
        self.tokens_list.pop(0)

    def advance_token(self, par_str_list):
        if len(self.tokens_list) == 0:
            print('[Log]:\tError_advance_token_failed')

        if (len(par_str_list) == 0) or (self.head_str() in par_str_list):  # 没有指定str，直接按照type解析
            self.parsed_list.append('<' + self.head_type() + '> ' + self.head_str() + ' </' + self.head_type() + '>')
            self.head_pop()
        else:
            print('[Log]:\tError in advance_token' + self.head_str())
            exit(0)

    # class
    def compile_class(self):
        self.parsed_list.append('<class>')
        self.advance_token('class')  # 'class'
        self.advance_token([])  # className
        self.advance_token('{')  # '{'

        while self.head_str() in ['static', 'field', 'constructor', 'function', 'method']:
            if self.head_str() in ['static', 'field']:  # classVar_dec*
                self.compile_class_var_dec()
            elif self.head_str() in ['constructor', 'function', 'method']:  # subroutineDec*
                self.compile_subroutine()

        self.advance_token('}')  # '}'
        self.parsed_list.append('</class>')

    # classVarDec
    def compile_class_var_dec(self):
        self.parsed_list.append('<classVarDec>')
        self.advance_token(['static', 'field'])  # 'static' | 'field'
        self.advance_token([])  # type
        self.advance_token([])  # varName

        while self.head_str() == ',':  # (',' varName)*
            self.advance_token(',')  # ','
            self.advance_token([])  # varName

        self.advance_token(';')  # ';'
        self.parsed_list.append('</classVarDec>')

    # subroutineDec
    def compile_subroutine(self):
        self.parsed_list.append('<subroutineDec>')

        self.advance_token(['constructor', 'function', 'method'])  # ('constructor'|'function'|'method')
        self.advance_token([])  # ('void'|type) type: 'int'|'char'|'boolean'|className
        self.advance_token([])  # subroutineName
        self.advance_token('(')  # '('
        self.compile_parameter_list()  # parameterList
        self.advance_token(')')

        # compile subroutineBody
        self.parsed_list.append('<subroutineBody>')
        self.advance_token('{')  # '{'
        while self.head_str() == 'var':  # varDec*
            self.compile_var_dec()
        self.compile_statements()  # statements
        self.advance_token('}')  # '}'
        self.parsed_list.append('</subroutineBody>')

        self.parsed_list.append('</subroutineDec>')

    # parameterList
    def compile_parameter_list(self):
        self.parsed_list.append('<parameterList>')

        if self.head_str() != ')':  # ((type varName) (',' type varName)*)?
            self.advance_token([])  # type
            self.advance_token([])  # varName
            while self.head_str() == ',':
                self.advance_token(',')  # ','
                self.advance_token([])  # type
                self.advance_token([])  # varName

        self.parsed_list.append('</parameterList>')

    # varDec
    def compile_var_dec(self):
        self.parsed_list.append('<varDec>')
        self.advance_token('var')  # 'var'
        self.advance_token([])  # ()type: 'int'|'char'|'boolean'|className
        self.advance_token([])  # varName
        while self.head_str() == ',':  # (',' varName)*
            self.advance_token(',')  # ','
            self.advance_token([])  # varName
        self.advance_token(';')  # ';'
        self.parsed_list.append('</varDec>')

    # statements
    def compile_statements(self):
        self.parsed_list.append('<statements>')  # statements
        while self.head_str() in ['let', 'if', 'while', 'do', 'return']:  # statements: statement
            if self.head_str() == 'let':  # letStatement
                self.compile_let()
            elif self.head_str() == 'if':  # ifStatement
                self.compile_if()
            elif self.head_str() == 'while':  # whileStatement
                self.compile_while()
            elif self.head_str() == 'do':  # doStatement
                self.compile_do()
            elif self.head_str() == 'return':  # returnStatement
                self.compile_return()
        self.parsed_list.append('</statements>')

    # doStatement
    def compile_do(self):
        self.parsed_list.append('<doStatement>')
        self.advance_token('do')  # 'do'

        # subroutineCall
        if self.tokens_list[1][0] == '(':
            self.advance_token([])  # subroutineName
        elif self.tokens_list[1][0] == '.':
            self.advance_token([])  # (className|varName)
            self.advance_token('.')  # '.'
            self.advance_token([])  # subroutineName
        self.advance_token('(')  # '('
        self.compile_expression_list()  # expressionList
        self.advance_token(')')  #

        self.advance_token(';')  # ';'
        self.parsed_list.append('</doStatement>')

    # letStatement
    def compile_let(self):
        self.parsed_list.append('<letStatement>')
        self.advance_token('let')  # 'let'
        self.advance_token([])  # varName
        if self.head_str() == '[':  # ('[' expression ']')?
            self.advance_token('[')  # '['
            self.compile_expression()  # expression
            self.advance_token(']')  # ']'
        self.advance_token('=')  # '='
        self.compile_expression()  # expression
        self.advance_token(';')  # ';'
        self.parsed_list.append('</letStatement>')

    # whileStatement
    def compile_while(self):
        self.parsed_list.append('<whileStatement>')
        self.advance_token('while')  # 'while'
        self.advance_token('(')  # '('
        self.compile_expression()  # expression
        self.advance_token(')')  # ')'
        self.advance_token('{')  # '{'
        self.compile_statements()  # statements
        self.advance_token('}')  # '}'
        self.parsed_list.append('</whileStatement>')

    # returnStatement
    def compile_return(self):
        self.parsed_list.append('<returnStatement>')
        self.advance_token('return')  # 'return'
        if self.head_str() != ';':  # expression?
            self.compile_expression()
        self.advance_token(';')  # ';'
        self.parsed_list.append('</returnStatement>')

    # ifStatement
    def compile_if(self):
        self.parsed_list.append('<ifStatement>')
        self.advance_token('if')  # 'if'
        self.advance_token('(')  # '('
        self.compile_expression()  # expression
        self.advance_token(')')  # ')'
        self.advance_token('{')  # '{'
        self.compile_statements()  # statements
        self.advance_token('}')  # '}'
        if self.head_str() == 'else':
            self.advance_token('else')
            self.advance_token('{')  # '{'
            self.compile_statements()  # statements
            self.advance_token('}')  # '}'
        self.parsed_list.append('</ifStatement>')

    def compile_expression(self):
        self.parsed_list.append('<expression>')
        op_jack = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
        self.compile_term()  # term
        while self.head_str() in op_jack:  # (op term)*
            self.advance_token(op_jack)  # op
            self.compile_term()  # term
        self.parsed_list.append('</expression>')

    def compile_term(self):
        self.parsed_list.append('<term>')
        unaryOp_jack = ['-', '~']
        if self.head_str() in unaryOp_jack:  # unary term
            self.advance_token(unaryOp_jack)
            self.compile_term()
        elif self.head_str() == '(':  # '(' expression ')'
            self.advance_token('(')  # '('
            self.compile_expression()  # expression
            self.advance_token(')')  # ')'
        elif self.tokens_list[1][0] in ['(', '.']:  # subroutineCall
            # subroutineCall
            if self.tokens_list[1][0] == '(':
                self.advance_token([])  # subroutineName
            elif self.tokens_list[1][0] == '.':
                self.advance_token([])  # (className|varName)
                self.advance_token('.')  # '.'
                self.advance_token([])  # subroutineName
            self.advance_token('(')  # '('
            self.compile_expression_list()  # expressionList
            self.advance_token(')')  #
        elif self.tokens_list[1][0] == '[':  # varName '[' expression ']'
            self.advance_token([])  # varName
            self.advance_token('[')  # '['
            self.compile_expression()  # expression
            self.advance_token(']')  # ']'
        else:
            self.advance_token([])  # integerConstant | stringConstant | keywordConstant | varName
        self.parsed_list.append('</term>')

    def compile_expression_list(self):
        self.parsed_list.append('<expressionList>')
        if self.head_str() != ')':  # (expression (',' expression)*)?
            self.compile_expression()  # expression
            while self.head_str() == ',':  # (',' expression)*
                self.advance_token(',')  # ','
                self.compile_expression()  # expression
        self.parsed_list.append('</expressionList>')


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


if __name__ == '__main__':
    print('[Warning]:\tthis script is not mean to used separately, use JackCompiler.py instead.\n')
