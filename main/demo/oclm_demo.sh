#!/bin/bash

set -x
set -e

nbest=$1
tst=$2
datapath=$3

##change working dir
pushd main

echo ------------------
echo "Demo of OCLM"
echo ------------------
fold=1
machines=TBD
# rm logger if found
export LD_LIBRARY_PATH=/usr/local/lib/fst
python ../../demo.py --test ${datapath}/${fold}${tst} --eeg eeg_data/EEGEvidence.txt-high --nbest $nbest --machines ${machines}

