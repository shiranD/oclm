#!/bin/bash
set -x
export LD_LIBRARY_PATH=/usr/local/lib/fst
syms=$1
echo -e "0\t0\t#\t#" > sig.txt
for i in f u l t o n c y g r a d j s i v e p m h k x w b z q
do
  echo -e "0\t0\t${i}\t${i}" >> sig.txt
done
echo -e "0\t1\t#\t#" >> sig.txt
for i in f u l t o n c y g r a d j s i v e p m h k x w b z q
do
  echo -e "1\t2\t${i}\t<epsilon>" >> sig.txt
done
echo -e "1" >> sig.txt
for i in f u l t o n c y g r a d j s i v e p m h k x w b z q
do
  echo -e "2\t2\t${i}\t<epsilon>" >> sig.txt
done
echo -e "2" >> sig.txt

fstcompile --isymbols=${syms} --osymbols=${syms} --keep_isymbols --keep_osymbols sig.txt | fstarcsort > machines/ch_before_last_space.fst
rm sig.txt
