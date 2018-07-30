#!/bin/bash
crp=$1
ord=5
syms=$2
farcompilestrings -symbols=${syms} -keep_symbols=1 $crp >$crp.far
ngramcount -order=$ord $crp.far >$crp.cnts
ngrammake --method=kneser_ney $crp.cnts machines/word_lm.fst
rm $crp.far
rm $crp.cnts

