#!/bin/bash
set -x
export LD_LIBRARY_PATH=/usr/local/lib/fst
file=$1
symsw=$2
symsc=$3
name=$4
ord=5
# compile to generate an lm
farcompilestrings -symbols=${symsc} -keep_symbols=1 $file >$file.far
ngramcount -order=$ord $file.far >$file.cnts
ngrammake --method=kneser_ney $file.cnts $file.fst

# make and anything to eps ch-wd
# compose with anything to eps
epsfile=eps.txt
rm $epsfile
for i in f u l t o n c y g r a d j s i v e p m h k x w b z q
do
  echo -e "0\t0\t${i}\t<epsilon>" >> $epsfile
done
echo -e "0" >> $epsfile
fstcompile --isymbols=${symsc} --osymbols=${symsw} --keep_isymbols --keep_osymbols $epsfile | fstdeterminize | fstminimize | fstarcsort > $epsfile.fst
fstcompose $file.fst $epsfile.fst > oeps.fst

# unke space unk and concat and apply closure
unkfile=unk.txt
echo -e "0\t1\t#\t<unk>" > $unkfile
echo -e "1" >> $unkfile
fstcompile --isymbols=${symsc} --osymbols=${symsw} --keep_isymbols --keep_osymbols $unkfile | fstdeterminize | fstminimize | fstarcsort > $unkfile.fst
fstconcat oeps.fst $unkfile.fst | fstrmepsilon | fstclosure > machines/$name.fst

# compose with the outcome and space to unk ch-wd
# add closure
rm $file.far
rm $file.cnts
rm $epsfile
rm oeps.fst
rm $unkfile
rm $epsfile.fst
rm $unkfile.fst 
rm $file
rm $file.fst
