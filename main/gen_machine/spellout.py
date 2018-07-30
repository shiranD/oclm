#!/usr/local/bin/python
import sys
import pywrapfst as fst
import copy
"""spellout out machine traslates words back to letter sequences
some words may contain symbols the are not found in the letter symbol set
therefore they are further parsed to map them to the letter symbol set"""

def dig2word(w):
    new_w = ""
    for ltr in w:
        if ltr.isdigit():
            if ltr == "0":
                new_w+="#oh"
            elif ltr == "1":
                new_w+="#one"
            elif ltr == "2":
                new_w+="#two"
            elif ltr == "3":
                new_w+="#three"
            elif ltr == "4":
                new_w+="#four"
            elif ltr == "5":
                new_w+="#five"
            elif ltr == "6":
                new_w+="#six"
            elif ltr == "7":
                new_w+="#seven"
            elif ltr == "8":
                new_w+="#eight"
            elif ltr == "9":
                new_w+="#nine"
        else:
            new_w+=ltr
    return new_w

def spellout_machine(wrdfname, ltr2wrdfst):
  
    lm = fst.Fst.read(ltr2wrdfst)
    s_in = lm.output_symbols()
    s_out = lm.input_symbols()
    
    letter = fst.Fst()
    letter.set_input_symbols(s_in)
    letter.set_output_symbols(s_out)
    letter.add_state()

    for word in open(wrdfname, "r").readlines():
        word = word.strip()
        orig = copy.copy(word)
#        word = list(word)
        word+="#"
        #word = dig2word(word)
        nletter = fst.Fst()
        nletter.set_input_symbols(s_in)
        nletter.set_output_symbols(s_out)
        nletter.add_state()
        for i,ltr in enumerate(word):
            nletter.add_state()
            code2 = s_out.find(ltr)
            if i==0:
                nletter.set_start(0)
                code1 = s_in.find(orig)
                nletter.add_arc(i, fst.Arc(code1, code2, None, i+1))
            else:
                code1 = s_in.find("<epsilon>")
                nletter.add_arc(i, fst.Arc(code1, code2, None, i+1))
        nletter.set_final(i+1)
        letter.union(nletter)
    letter.rmepsilon()
    letter.write("spellout.fst")

if __name__ == "__main__":
   spellout_machine(sys.argv[1], sys.argv[2])
