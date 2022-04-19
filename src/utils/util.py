import os


def is_blank(input_data):
    count = 0
    blank = ' '
    for char in input_data:
        if char == blank:
            count += 1

    return True if count == len(input_data) or input_data == '' else input_data


def clear_tempfiles():
    for file in os.listdir():
        if 'TEMP_MPY_wvf' in file:
            os.remove(file)
