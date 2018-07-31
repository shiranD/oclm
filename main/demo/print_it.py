#!/usr/bin/env python
# coding=utf-8

# based on termgraph.py - draw basic graphs on terminal
# https://github.com/mkaz/termgraph

from __future__ import division
from __future__ import print_function
import sys

# TODO: change tick character
green = '\033[31m'
black = '\033[30m'
blue = '\033[94m'
reset = '\033[0m'
bold = '\033[01m'
lightgrey = '\033[92m'
lightgrey = '\033[33m'
TICK_o = '▧'
TICK = green + TICK_o + reset
TICKW = blue + TICK_o + reset
TICK_S = "\xe2\x80\x87"
#TICK = '▇i'
#TICK_S = ' '
SM_TICK_o = '▏'
SM_TICKW = blue + SM_TICK_o + reset
SM_TICK = green + SM_TICK_o + reset

# sample bar chart data
# labels = ['2007', '2008', '2009', '2010', '2011']
# data = [183.32, 231.23, 16.43, 50.21, 508.97]

try:
    range = xrange
except NameError:
    pass


def print_evidence(eeg, past, target):
    if eeg == '[]':
        return
    labels = [ch for ch, pr in sorted(eeg, key=lambda pair: pair[1], reverse=True)]
    if not past:
        current = []
        print("\n\n")
        for label in labels:
            if label == target:
                new = "     " + bold + label + reset + " "
                current.append(new)
                print(new)
            else:
                new = "     " + lightgrey + label + reset + " "
                current.append(new)
                print(new)
    else:
        current = []
        for past_level, label in zip(past, labels):
            if label == target:
                new = past_level + bold + label + reset + " "
                current.append(new)
                print(new)
            else:
                new = past_level + lightgrey + label + reset + " "
                current.append(new)
                print(new)
    print("\n\n")
    return current


def normalize(data, width):
    min_dat = min(data)
    # We offset by the mininum if there's a negative
    if min_dat < 0:
        min_dat = abs(min_dat)
        off_data = [_d + min_dat for _d in data]
    else:
        off_data = data
    min_dat = min(off_data)
    max_dat = max(off_data)

    if max_dat < width:
        # Don't need to normalize if the max value
        # is less than the width we allow.
        return off_data

    #avg_dat = sum(off_data) / float(len(off_data))
    if max_dat == min_dat and len(data) == 1:
        return [width for _v in off_data]
    else:
        norm_factor = width / float(max_dat - min_dat)
        return [(_v - min_dat) * norm_factor for _v in off_data]


def horiontal_rows(labels, data, normal_dat, labels1, data1, normal_dat1, args):
    val_min = min(data)
    val1_min = min(data1)

    for i in range(max(len(labels), len(labels1))):
        try:
            label = "     {:2} ".format(labels[i])
            value = data[i]
            num_blocks = normal_dat[i]
        except:
            label = ""
            value = ""
            num_blocks = 0
        try:
            label_w = labels1[i]
            val_w = data1[i]
            num_blocks2 = normal_dat1[i]
        except:
            label_w = ""
            val_w = ""
            num_blocks2 = 0
        tail = ' {}{}'.format(args['format'].format(value), args['suffix'])
        yield (label, value, int(num_blocks), val_min, label_w, val_w, int(num_blocks2), val1_min, tail)


def print_row(label, value, num_blocks, val_min, label_w, val_w, num_blocks1, val1_min, tail):
    """A method to print a row for a horizontal graphs.
    i.e:
    1: ▇▇ 2
    2: ▇▇▇ 3
    3: ▇▇▇▇ 4
    """
    MAX = 50
    w_len = 20
    ch_len = 2 + 5 + 1
    w_left = w_len - len(label_w)
    if label == "":
        for i in range(MAX + ch_len + w_left + MAX):
            if i < MAX + ch_len:
                sys.stdout.write(TICK_S)
            elif i == MAX + ch_len:
                if label_w != "":
                    sys.stdout.write(label_w)
                else:
                    break
            elif i > MAX + ch_len and i < MAX + ch_len + w_left:
                sys.stdout.write(TICK_S)
            elif i > MAX + w_left + ch_len and num_blocks1 < 1 and (val_w > val1_min or val_w > 0):
                sys.stdout.write(SM_TICKW)
                break
            elif i > MAX + w_left + ch_len and i < MAX + ch_len + w_left + num_blocks1 + 1:
                sys.stdout.write(TICKW)
    else:
        print(label, end="")
        if num_blocks < 1 and (value > val_min or value > 0):
            # Print something if it's not the smallest
            # and the normal value is less than one.
            sys.stdout.write(SM_TICK)
            for i in range(MAX + w_left + MAX):
                if i < MAX - 1:
                    sys.stdout.write(TICK_S)
                if i == MAX - 1:
                    if label_w != "":
                        sys.stdout.write(label_w)
                    else:
                        break
                elif i > MAX - 1 and i < MAX - 1 + w_left:
                    sys.stdout.write(TICK_S)
                elif i > MAX - 1 + w_left and num_blocks1 < 1 and (val_w > val1_min or val_w > 0):
                    sys.stdout.write(SM_TICKW)
                    break
                elif i > MAX - 1 + w_left and i < MAX - 1 + w_left + num_blocks1 + 1:
                    sys.stdout.write(TICKW)
        else:
            for i in range(MAX + w_left + MAX):
                if i < num_blocks:
                    sys.stdout.write(TICK)
                elif i < MAX:
                    sys.stdout.write(TICK_S)
                elif i == MAX:
                    if label_w != "":
                        sys.stdout.write(label_w)
                    else:
                        break
                elif i > MAX and i < MAX + w_left:
                    sys.stdout.write(TICK_S)
                elif i > MAX + w_left and num_blocks1 < 1 and (val_w > val1_min or val_w > 0):
                    sys.stdout.write(SM_TICKW)
                    break
                elif i > MAX + w_left and i < MAX + w_left + num_blocks1 + 1:
                    sys.stdout.write(TICKW)
    print(tail)


def histit(data, labels, data1, labels1):
    # Normalize data, handle negatives.
    args = {'width': 40, 'format': '', 'ignore_labels': False, 'suffix': ''}
    normal_dat = normalize(data, args['width'])
    normal_dat1 = normalize(data1, args['width'])

    # Generate data for a row.
    for row in horiontal_rows(labels, data, normal_dat, labels1, data1, normal_dat1, args):
        # Print the row
        print_row(*row)
