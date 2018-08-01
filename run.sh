#!/bin/bash

# This is the main code to prepare the input for the OCLM code
 
set -x
set -e

test_name=_test.txt
train_name=_train.txt
corpus=TBD # corpus of sentences
# make the following folders
mkdir -p data
mkdir -p json_output
datapath=../data
out=../json_output
ch_sym=../ch_syms.txt
folds=0
nbest=1 # 1-3 is optimal

python3 split.py --train $train_name --test $test_name --fdata $corpus --odir $datapath/ --folds $folds
main/./oclm_train.sh $ch_sym $train_name $datapath $out $folds
main/./oclm_test.sh $nbest $test_name $datapath $out $folds
# Demo should be actively copied from demo dir to main dir
#main/./oclm_demo.sh $nbest $test_name $datapath
