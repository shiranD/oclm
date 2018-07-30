#!/bin/bash
set -x
export LD_LIBRARY_PATH=/usr/local/lib/fst
syms=$1
special=$2
echo -e "0\t0\t<sigma>\t<epsilon>\n0\t1\t<sigma>\t<sigma>\n1" > sig.txt
fstcompile --isymbols=${syms} --osymbols=${syms} --keep_isymbols --keep_osymbols sig.txt | fstspecial --fst_type=sigma --sigma_fst_sigma_label=$special --sigma_fst_rewrite_mode="always" > machines/ltr_dist.sigma.fst
rm sig.txt
