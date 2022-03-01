#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""No description"""

__author__ = 'eric'

import os


def main():
    temp_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    print(temp_list)
    my_func(temp_list)
    print(temp_list)

    my_func_2(None)


def my_func(par_1):
    par_1.pop()


def my_func_2(temp):
    print(temp)


if __name__ == '__main__':
    main()
