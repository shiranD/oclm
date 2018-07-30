#!/bin/bash
set -x
export LD_LIBRARY_PATH=/usr/local/lib/fst
syms=$1
special=$2
for i in 0 1 2 3 4 5 6 7 8 9
do
  echo -e "${i}\t$(($i+1))\t<sigma>\t<sigma>" >> sig.txt  
  echo -e "${i}\t$(($i+1))\t<epsilon>\t<epsilon>" >> sig.txt  
done
echo -e "10" >> sig.txt

fstcompile --isymbols=${syms} --osymbols=${syms} --keep_isymbols --keep_osymbols sig.txt | fstarcsort |  fstspecial --fst_type=sigma --sigma_fst_sigma_label=$special --sigma_fst_rewrite_mode="always" > machines/length_machine.sigma.fst
rm sig.txt
