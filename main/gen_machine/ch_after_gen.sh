#!/bin/bash
set -x
export LD_LIBRARY_PATH=/usr/local/lib/fst
syms=$1
special=$2
echo -e "0\t1\t<epsilon>\t<epsilon>" > sig.txt
echo -e "0\t2\t<epsilon>\t<epsilon>" >> sig.txt
echo -e "1\t2\t#\t<epsilon>" >> sig.txt
echo -e "1\t1\t<sigma>\t<epsilon>" >> sig.txt
for i in f u l t o n c y g r a d j s i v e p m h k x w b z q
do
  echo -e "2\t2\t${i}\t${i}" >> sig.txt
done
echo -e "2" >> sig.txt

fstcompile --isymbols=${syms} --osymbols=${syms} --keep_isymbols --keep_osymbols sig.txt | fstspecial --fst_type=sigma --sigma_fst_sigma_label=$special --sigma_fst_rewrite_mode="always" > machines/ch_after_last_space.sigma.fst
rm sig.txt
