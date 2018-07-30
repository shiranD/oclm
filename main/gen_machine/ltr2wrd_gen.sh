#!/bin/bash
set -x
export LD_LIBRARY_PATH=/usr/local/lib/fst
file=$1
symsw=$2
symsc=$3
name=$4
fstcompile --isymbols=${symsc} --osymbols=${symsw} --keep_isymbols --keep_osymbols $file | fstdeterminize | fstminimize | fstarcsort > machines/$name.fst
#rm $file
