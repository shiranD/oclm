#!/bin/bash
crp=$1
syms=$2
ord=5
farcompilestrings -symbols=${syms} -keep_symbols=1 $crp >$crp.far
ngramcount --backoff_label=200 -order=$ord $crp.far >$crp.cnts
ngrammake --method=katz $crp.cnts $crp.fst
mv $crp.fst machines/ltr_lm.fst
rm $crp.cnts
rm $crp
rm $crp.far
