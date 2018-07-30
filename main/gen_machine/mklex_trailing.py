#! /usr/bin/env python

import sys

eps = '<epsilon>'
spa = '#'
phi = '<phi>'
rho = '<rho>'
unk = '<unk>'
cost = 1
printable = 'abcdefghijklmnopqrstuvwxyz'

def make_lexicon(ifile):
    s = 2
    for line in ifile:
        word = line.strip()
        if word.startswith('<'):
            continue  # special
        for i, letter in enumerate(word):
            if i == 0:
                print 0, s, letter, eps
            else:
                print s, s + 1, letter, eps
                s = s + 1
        print s, 0, spa, word           # whitespace required (even at the end)
        s = s + 1
    print 0

if __name__ == '__main__':
    make_lexicon(sys.stdin)

