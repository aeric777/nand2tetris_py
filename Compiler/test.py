import re


def index_all(main_str, sub_str):
    return [each.start() for each in re.finditer(sub_str, main_str)]


def index_all_end(main_str, sub_str):
    starts = index_all(main_str, sub_str)
    return [start + len(sub_str) - 1 for start in starts]


if __name__ == '__main__':
    line_1 = 'str = "this is a comment// 123" + "string part two"'
    line_2 = 'str = "test /** test /*"'
    split_quote = line_1.split('\"')
    print(split_quote)
    num_flag = 0
    res_list = []
    for each_split in split_quote:
        if num_flag % 2 == 0:
            num_flag = num_flag + 1
        else:
            res_list.append(each_split)
            num_flag = num_flag + 1

    print(res_list)
