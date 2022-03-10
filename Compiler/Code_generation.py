#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description:
    generate .vm code using the parsing tree build by syntax_analyzer
Module:
    SymbolTable, VMWriter
Recommended OS:
    Linux
"""

__author__ = 'eric'


# # ----------------------------------------------------------
# # Description:
# #       generating vm code
# # Output:
# #       vm_list
# def code_generation():
#     vm_list = []
#     return vm_list


# ----------------------------------------------------------
# Class Description:
# Instantiate:          CompilationEngineToVM(tokens_list)
class CompilationEngineToVM(object):
    def __init__(self, tokens_list):
        # create a new list by using copy() explicitly, or your operation will be done on original tokens_list[]
        self.tokens_list = tokens_list.copy()  # tokenized_list is a list of tuple[('token', 'token_type')]
        # symbol_table
        self.global_table = SymbolTable()  # symbol_table for class scope
        self.sub_table = SymbolTable()  # symbol_table for each subroutine scope
        # vm_writer
        self.vm_write = VMWriter()  # write vm_file
        # more info used for compiling class
        self.class_name = ''
        self.subroutine_type = ''
        self.func_name = ''
        self.while_index = 0  # maintain the index of the label used in while_statement and if_statement
        self.if_index = 0

        # ---* main compilation engine process *---
        self.compile_class()
        if len(self.tokens_list) != 0:
            print('[Log]:\tError_unparsered_token:', self.tokens_list)

    # ----------------------------------------------------------
    # Description:  return the vm_list
    def get_vm_list(self):
        return self.vm_write.get_vm_list()

    # ----------------------------------------------------------
    # Description:  return the first token of the tokens_list
    def head_str(self):
        return self.tokens_list[0][0]

    # ----------------------------------------------------------
    # Description:  return the first token's type of the tokens_list
    def head_type(self):  # keyword | symbol | integerConstant | stringConstant | identifier
        return self.tokens_list[0][1]

    # ----------------------------------------------------------
    # Description:  pop out the first token
    def head_pop(self):
        self.tokens_list.pop(0)

    # ----------------------------------------------------------
    # Description:  validating this token using str_list and type_list, pop the first token
    # Input:
    #   str_list    - specify a list of valid str
    #   type_list   - specify a list of valid type
    def advance_token(self, str_list, type_list):
        if len(self.tokens_list) == 0:
            print('[Log]:\tError_advance_token_failed')

        # no specified str_list or the first token conforms the requirements given by str_list，
        if (len(str_list) == 0) or (self.head_str() in str_list):
            # no specified type_list or the first token's type conforms the requirements given by type_list，
            # do nothing and execute pop() directly
            if (len(type_list) == 0) or (self.head_type() in type_list):
                self.head_pop()
            else:
                print('[Log]:\tError_in_advance_token_type, valid type: ', type_list,
                      '\ntoken: ' + self.head_str() + ' type: ' + self.head_type())
                exit(0)
        else:
            print('[Log]:\tError_in_advance_token_str, valid str: ', str_list,
                  '\ntoken: ' + self.head_str() + ' type: ' + self.head_type())
            exit(0)

    # ----------------------------------------------------------
    # class
    def compile_class(self):
        self.advance_token(['class'], ['keyword'])  # 'class'
        self.class_name = self.head_str()  # record class_name
        self.advance_token([], ['identifier'])  # className
        self.advance_token(['{'], ['symbol'])  # '{'

        while self.head_str() in ['static', 'field', 'constructor', 'function', 'method']:
            if self.head_str() in ['static', 'field']:  # classVar_dec*
                self.compile_class_var_dec()
            elif self.head_str() in ['constructor', 'function', 'method']:  # subroutineDec*
                self.compile_subroutine_dec()

        self.advance_token(['}'], ['symbol'])  # '}'

    # ----------------------------------------------------------
    # classVarDec
    def compile_class_var_dec(self):
        _kind = self.head_str()
        if _kind == 'field':
            _kind = 'this'
        self.advance_token(['static', 'field'], ['keyword'])  # 'static' | 'field'
        _type = self.head_str()
        self.advance_token([], ['keyword', 'identifier'])  # type
        _name = self.head_str()
        self.advance_token([], ['identifier'])  # varName
        self.global_table.define(_name, _type, _kind)

        while self.head_str() == ',':  # (',' varName)*
            self.advance_token([','], ['symbol'])  # ','
            _name = self.head_str()
            self.advance_token([], ['identifier'])  # varName
            self.global_table.define(_name, _type, _kind)

        self.advance_token([';'], ['symbol'])  # ';'

    # ----------------------------------------------------------
    # subroutineDec
    def compile_subroutine_dec(self):
        self.sub_table.start_subroutine()  # reset sub_table for this subroutine
        local_var_cnt = 0  # reset the count of local variables for this subroutine

        self.subroutine_type = self.head_str()  # record the type of this subroutine
        self.advance_token(['constructor', 'function', 'method'], ['keyword'])  # ('constructor'|'function'|'method')

        # ('void'|type) type: 'int'|'char'|'boolean'|className
        self.advance_token([], ['keyword', 'identifier'])  # ('void'|type)
        # if subroutine type is constructor, this func_name has to be new
        self.func_name = self.class_name + '.' + self.head_str()  # record function name
        self.advance_token([], ['identifier'])  # subroutineName
        self.advance_token(['('], ['symbol'])  # '('
        self.compile_parameter_list()  # parameterList
        self.advance_token([')'], ['symbol'])

        # compile subroutineBody
        self.advance_token(['{'], ['symbol'])  # '{'

        # varDec has to on ahead of statements
        while self.head_str() == 'var':  # varDec*
            local_var_cnt += self.compile_var_dec()

        self.vm_write.write_function(self.func_name, local_var_cnt)  # function f n
        if self.subroutine_type == 'constructor':
            # as a callee, the constructor need to allocate a memory block for the new object,
            # and set the base of 'this' segment to point at base of block memory that just allocated
            field_num = self.global_table.kind_count['this']  # only consider the number of field variables
            # all build-in type in .jack language can be represented by a 16-bit word,
            # if type of this field variable is object, the value of that field variable is the base addr of that obj,
            # which can also be represented by a 16-bit word
            self.vm_write.write_push('constant', field_num)
            self.vm_write.write_call('Memory.alloc', 1)
            self.vm_write.write_pop('pointer', 0)
        elif self.subroutine_type == 'method':
            # as a callee, the method is supposed to set the base of 'this' segment to argument 0
            self.vm_write.write_push('argument', 0)
            self.vm_write.write_pop('pointer', 0)

        self.compile_statements()  # statements
        self.advance_token(['}'], ['symbol'])  # '}'

    # ----------------------------------------------------------
    # parameterList
    # the variables in parameterList should be count on subroutine symbol_table
    def compile_parameter_list(self):
        if self.subroutine_type == 'method':  # first parameter of method has to be a 'this' pointer
            # first parameter should be an implicit 'this'
            self.sub_table.define('this', self.class_name, 'argument')
            # even if there is no parameter given to this method

        if self.head_str() != ')':  # ((type varName) (',' type varName)*)?
            _type = self.head_str()
            self.advance_token([], ['keyword', 'identifier'])  # type
            _name = self.head_str()
            self.advance_token([], ['identifier'])  # varName
            self.sub_table.define(_name, _type, 'argument')

            while self.head_str() == ',':
                self.advance_token([','], ['symbol'])  # ','
                _type = self.head_str()
                self.advance_token([], ['keyword', 'identifier'])  # type
                _name = self.head_str()
                self.advance_token([], ['identifier'])  # varName
                self.sub_table.define(_name, _type, 'argument')

    # ----------------------------------------------------------
    # varDec
    # the variables in varDec should be count on subroutine symbol_table
    def compile_var_dec(self):
        local_var_cnt = 0
        self.advance_token(['var'], ['keyword'])  # 'var'

        _type = self.head_str()
        self.advance_token([], ['keyword', 'identifier'])  # ()type: 'int'|'char'|'boolean'|className
        _name = self.head_str()
        self.advance_token([], ['identifier'])  # varName
        self.sub_table.define(_name, _type, 'local')
        local_var_cnt += 1

        while self.head_str() == ',':  # (',' varName)*
            self.advance_token([','], ['symbol'])  # ','
            _name = self.head_str()
            self.advance_token([], ['identifier'])  # varName
            self.sub_table.define(_name, _type, 'local')
            local_var_cnt += 1

        self.advance_token([';'], ['symbol'])  # ';'
        return local_var_cnt

    # ----------------------------------------------------------
    # statements
    def compile_statements(self):
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

    # ----------------------------------------------------------
    # doStatement
    def compile_do(self):
        self.advance_token(['do'], ['keyword'])  # 'do'
        self.compile_subroutine_call()  # subroutineCall
        self.advance_token([';'], ['symbol'])  # ';'
        self.vm_write.write_pop('temp', 0)  # pop a useless value after void function return

    # ----------------------------------------------------------
    # subroutineCall
    # situations of calling subroutine：
    #   subroutineName()            - method of this class
    #   varName.subroutineName()    - method of other class
    #   className.subroutineName()  - function of whatever class(including constructor, if subroutineName is new)
    # Notice:
    #   when calling subroutine, there is no need to distinguish function and constructor,
    #   since you already insert the vm.code that allocate memory in the vm.code part that belong to this constructor
    def compile_subroutine_call(self):
        expression_num = 0
        if self.tokens_list[1][0] == '(':  # subroutineName(expressionList)
            # 1. as a caller of a method, you are supposed to push the obj as the first and implicit argument.
            # 2. as the syntax specified, the only situation when you can call a subroutine like subroutineName(expressionList)
            # is when this subroutine is a method in this class
            # you are supposed to push this(pointer 0) as the first and implicit argument
            self.vm_write.write_push('pointer', 0)
            expression_num += 1

            self.subroutine_type = 'method'
            self.func_name = self.class_name + '.' + self.head_str()
            self.advance_token([], ['identifier'])  # subroutineName
        elif self.tokens_list[1][0] == '.':  # (className|varName).subroutineName(expressionList)
            _type, _kind, _index, if_exist = self.info_of_identifier(self.head_str())
            if if_exist:  # identifier in symbol_table, str is a variable, means this subroutine is a method
                # _type have been confirmed
                # as a caller of a method, you are supposed to push the obj as the first and implicit argument
                self.vm_write.write_push(_kind, _index)
                expression_num += 1
                self.subroutine_type = 'method'
            else:  # identifier not in symbol_table, str is className
                _type = self.head_str()
                # as a caller of a function or constructor,
                # you treat function and constructor with no difference
                # the only thing for sure is that a constructor return the addr of obj it just created
                self.subroutine_type = 'function'  # function or constructor
            self.advance_token([], ['identifier'])  # (className|varName)
            self.advance_token(['.'], ['symbol'])  # '.'

            if self.head_str() == 'new':
                self.subroutine_type = 'constructor'
            self.func_name = _type + '.' + self.head_str()
            self.advance_token([], ['identifier'])  # subroutineName

        self.advance_token(['('], ['symbol'])  # '('
        expression_num += self.compile_expression_list()  # expressionList
        self.advance_token([')'], ['symbol'])  # ')'
        self.vm_write.write_call(self.func_name, expression_num)

    # ----------------------------------------------------------
    # check if identifier is in symbol table, return specified info if it does
    # Return:   _type, _kind, _index, if_exist
    def info_of_identifier(self, identifier):
        if identifier in self.sub_table.table:  # identifier found in sub_table
            return [self.sub_table.which_type(identifier), self.sub_table.which_kind(identifier),
                    self.sub_table.which_index(identifier), True]
        elif identifier in self.global_table.table:  # identifier found in global_table
            return [self.global_table.which_type(identifier), self.global_table.which_kind(identifier),
                    self.global_table.which_index(identifier), True]
        else:    # identifier not found
            return [None, None, None, False]

    # ----------------------------------------------------------
    # letStatement
    def compile_let(self):
        arr_manipulation = 0

        self.advance_token(['let'], ['keyword'])  # 'let'
        temp_var_name = self.head_str()  # record variable that is given value to
        self.advance_token([], ['identifier'])  # varName
        _type, _kind, _index, if_exist = self.info_of_identifier(temp_var_name)
        if not if_exist:
            print('[Log]:\tError_invalid_variable_' + temp_var_name)
            exit(0)

        if self.head_str() == '[':  # ('[' expression ']')?
            # notice: when the code you are about to compile is something like: 'let arr[exp1] = exp2'
            # you are not allowed to use 'pointer 1' before calculating the value of exp2
            # since you might use 'pointer 1' in your calculation of exp2 either, which will definitely cause a crash
            arr_manipulation = 1
            self.vm_write.write_push(_kind, _index)

            self.advance_token(['['], ['symbol'])  # '['
            self.compile_expression()  # expression
            self.advance_token([']'], ['symbol'])  # ']'

            self.vm_write.write_arithmetic('add')

        self.advance_token(['='], ['symbol'])  # '='
        self.compile_expression()  # expression

        if arr_manipulation:
            self.vm_write.write_pop('temp', 0)
            self.vm_write.write_pop('pointer', 1)
            self.vm_write.write_push('temp', 0)
            self.vm_write.write_pop('that', 0)
        else:
            self.vm_write.write_pop(_kind, _index)

        self.advance_token([';'], ['symbol'])  # ';'

    # ----------------------------------------------------------
    # whileStatement
    def compile_while(self):
        while_cnt = self.while_index
        self.while_index += 1
        label_start = 'label_while_start_' + str(while_cnt)
        label_end = 'label_while_end_' + str(while_cnt)
        self.vm_write.write_label(label_start)  # label label_start
        self.advance_token(['while'], ['keyword'])  # 'while'

        self.advance_token(['('], ['symbol'])  # '('
        self.compile_expression()  # expression
        self.advance_token([')'], ['symbol'])  # ')'

        self.vm_write.write_arithmetic('not')  # not, (bit-wise operation)
        self.vm_write.write_if(label_end)  # if-goto label_end, (jump if top value of stack is not zero-False)

        self.advance_token(['{'], ['symbol'])  # '{'
        self.compile_statements()  # statements
        self.advance_token(['}'], ['symbol'])  # '}'

        self.vm_write.write_goto(label_start)  # goto label_start, (jump with no condition)
        self.vm_write.write_label(label_end)  # label label_end

    # ----------------------------------------------------------
    # returnStatement
    def compile_return(self):
        self.advance_token(['return'], ['keyword'])  # 'return'
        if self.head_str() != ';':  # expression?
            self.compile_expression()
        else:
            self.vm_write.write_push('constant', 0)

        self.advance_token([';'], ['symbol'])  # ';'
        self.vm_write.write_return()  # return

    # ----------------------------------------------------------
    # ifStatement
    def compile_if(self):
        if_cnt = self.if_index
        self.if_index += 1
        label_if = 'label_if_' + str(if_cnt)
        label_else = 'label_else_' + str(if_cnt)

        self.advance_token(['if'], ['keyword'])  # 'if'
        self.advance_token(['('], ['symbol'])  # '('
        self.compile_expression()  # expression
        self.advance_token([')'], ['symbol'])  # ')'

        self.vm_write.write_arithmetic('not')  # not
        self.vm_write.write_if(label_if)

        self.advance_token(['{'], ['symbol'])  # '{'
        self.compile_statements()  # statements
        self.advance_token(['}'], ['symbol'])  # '}'

        self.vm_write.write_goto(label_else)
        self.vm_write.write_label(label_if)

        if self.head_str() == 'else':
            self.advance_token(['else'], ['keyword'])
            self.advance_token(['{'], ['symbol'])  # '{'
            self.compile_statements()  # statements
            self.advance_token(['}'], ['symbol'])  # '}'

        self.vm_write.write_label(label_else)

    # ----------------------------------------------------------
    # compile expression, leave the result of this expression on the stack
    def compile_expression(self):
        op_jack = {'+': 'add',
                   '-': 'sub',
                   '*': 'call Math.multiply 2',
                   '/': 'call Math.divide 2',
                   '&': 'and',
                   '|': 'or',
                   '<': 'lt',
                   '>': 'gt',
                   '=': 'eq'}
        self.compile_term()  # term
        while self.head_str() in op_jack:  # (op term)*
            temp_op = self.head_str()
            self.advance_token(op_jack, ['symbol'])  # op
            self.compile_term()  # term
            self.vm_write.write_arithmetic(op_jack[temp_op])  # write arithmetic command

    def compile_term(self):
        unaryOp_jack = {'-': 'neg', '~': 'not'}
        key_word_constant = ['true', 'false', 'null', 'this']
        if self.head_str() in unaryOp_jack:  # unaryOp term
            temp_cmd = unaryOp_jack[self.head_str()]
            self.advance_token(unaryOp_jack, ['symbol'])
            self.compile_term()
            self.vm_write.write_arithmetic(temp_cmd)

        elif self.head_str() == '(':  # '(' expression ')'
            self.advance_token(['('], ['symbol'])  # '('
            self.compile_expression()  # expression
            self.advance_token([')'], ['symbol'])  # ')'

        elif self.tokens_list[1][0] in ['(', '.']:  # subroutineCall
            self.compile_subroutine_call()

        elif self.tokens_list[1][0] == '[':  # varName '[' expression ']'
            _type, _kind, _index, if_exist = self.info_of_identifier(self.head_str())
            if not if_exist:
                print('[Log]:\tError_no_such_varName_' + self.head_str())
                exit(0)
            self.vm_write.write_push(_kind, _index)

            self.advance_token([], ['identifier'])  # varName
            self.advance_token(['['], ['symbol'])  # '['
            self.compile_expression()  # expression
            self.advance_token([']'], ['symbol'])  # ']'

            self.vm_write.write_arithmetic('add')
            self.vm_write.write_pop('pointer', 1)
            self.vm_write.write_push('that', 0)

        elif self.head_type() == 'identifier':  # varName
            _type, _kind, _index, if_exist = self.info_of_identifier(self.head_str())
            if if_exist:
                self.vm_write.write_push(_kind, _index)
                self.advance_token([], ['identifier'])
            else:
                print('[Log]:\tError_invalid_variable')
                exit(0)

        elif self.head_type() == 'keyword':  # keywordConstant
            if self.head_str() == 'true':  # push 1111111111111111
                self.vm_write.write_push('constant', 0)
                self.vm_write.write_arithmetic('not')
            elif self.head_str() in ['false', 'null']:  # push 0000000000000000
                self.vm_write.write_push('constant', 0)
            elif self.head_str() == 'this':  # push pointer 0
                self.vm_write.write_push('pointer', 0)
            self.advance_token(key_word_constant, ['keyword'])

        elif self.head_type() == 'stringConstant':  # stringConstant
            length = len(self.head_str())
            self.vm_write.write_push('constant', length)  # push constant length
            self.vm_write.write_call('String.new', 1)  # call String.new 1
            for each_alpha in self.head_str():
                self.vm_write.write_push('constant', ord(each_alpha))  # push constant ascii
                self.vm_write.write_call('String.appendChar', 2)  # call String.appendChar 2

            self.advance_token([], ['stringConstant'])

        elif self.head_type() == 'integerConstant':  # integerConstant
            self.vm_write.write_push('constant', self.head_str())
            self.advance_token([], ['integerConstant'])

    # ----------------------------------------------------------
    # expressionList
    # Return: expression_num(the number of expression in this list)
    def compile_expression_list(self):
        expression_num = 0
        if self.head_str() != ')':  # (expression (',' expression)*)?
            self.compile_expression()  # expression
            expression_num += 1
            while self.head_str() == ',':  # (',' expression)*
                self.advance_token([','], ['symbol'])  # ','
                self.compile_expression()  # expression
                expression_num += 1
        return expression_num


# ----------------------------------------------------------
# Class Description:
# Instantiate:          SymbolTable()
class SymbolTable(object):
    def __init__(self):
        self.table = {}  # {name : [type, kind, index]}
        # kind: ( static | field | argument | var)
        # Notice: in order to facilitate compile, count the 'field' and 'var' variable as 'this' and 'local',
        # since it would be easier to access that variable in VM segment using its _kind directly
        self.kind_count = {'static': 0,  # stands for   - static variable
                           'this': 0,  # stands for     - field variable
                           'argument': 0,  # stands for - argument variable
                           'local': 0}  # stands for    - var variable

    # ----------------------------------------------------------
    # Description:  start compiling a new subroutine, reset this symbol table(only sub table)
    def start_subroutine(self):
        self.table.clear()
        for each_key in self.kind_count.keys():
            self.kind_count[each_key] = 0

    # ----------------------------------------------------------
    # Description:  add a new variable into symbol_table, autonomously increase index according to its kind
    def define(self, _name, _type, _kind):  # using _ as prefix, or it will cause conflict with build-in identifiers
        self.table[_name] = [_type, _kind, self.kind_count[_kind]]
        self.kind_count[_kind] += 1

    # ----------------------------------------------------------
    def which_kind(self, name):
        _kind = None
        if name in self.table:
            _kind = self.table.get(name)[1]
        else:
            print('[Log]:\tError_no_such_identifier')
            exit(0)

        return _kind

    # ----------------------------------------------------------
    def which_type(self, name):
        _type = None
        if name in self.table:
            _type = self.table.get(name)[0]
        else:
            print('[Log]:\tError_no_such_identifier')
            exit(0)

        return _type

    # ----------------------------------------------------------
    def which_index(self, name):
        _index = None
        if name in self.table:
            _index = self.table.get(name)[2]
        else:
            print('[Log]:\tError_no_such_identifier')
            exit(0)

        return _index


# ----------------------------------------------------------
# Class Description:
# Instantiate:          VMWriter()
class VMWriter(object):
    def __init__(self):
        self.vm_list = []  # vm_list is list of str, each str is a line of final vm file

    def get_vm_list(self):
        return self.vm_list

    def write_push(self, segment, index):
        self.vm_list.append('push {0} {1}'.format(segment, str(index)))

    def write_pop(self, segment, index):
        self.vm_list.append('pop {0} {1}'.format(segment, str(index)))

    def write_arithmetic(self, cmd):
        self.vm_list.append(cmd)

    def write_label(self, label):
        self.vm_list.append('label {0}'.format(label))

    def write_goto(self, label):
        self.vm_list.append('goto {0}'.format(label))

    def write_if(self, label):
        self.vm_list.append('if-goto {0}'.format(label))

    def write_call(self, name, n_args):
        self.vm_list.append('call {0} {1}'.format(name, str(n_args)))

    def write_function(self, name, n_vars):
        self.vm_list.append('function {0} {1}'.format(name, str(n_vars)))

    def write_return(self):
        self.vm_list.append('return')


if __name__ == '__main__':
    print('[Warning]:\tthis script is not mean to used separately, use Compiler.py instead.\n')
