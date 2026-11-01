# Write a function that computes the size that a given folder occupies including
# all its subfolders and files using recursion without the use of “glob....” or
# “os.walk”. Have a look at “folder_operations.py” and “bowls_game.py” for hints.

import os
from pathlib import Path

def get_file_size_rf(loc):
    folder_list = os.listdir(loc)
    total_size = 0
    for f in folder_list:
        if os.path.isfile(f'{loc}/{f}'):
            total_size += os.path.getsize(f'{loc}/{f}')
        elif os.path.isdir(f'{loc}/{f}'):
            total_size += get_file_size_rf(os.path.join(loc, f))
        print(f'{f}: {total_size}')
    obj_count = len(folder_list)
    return total_size


def get_dir_size():
    cwd = os.getcwd()
    # cwd = Path(r'D:\Advanced Analytics - Big Data\test')
    print(f'current working dir: {cwd}')
    size_sum = 0
    size_sum = get_file_size_rf(cwd)
    print(f'Dir size is: {size_sum}')

get_dir_size()