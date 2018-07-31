#!/bin/bash

set -x
set -e

nbest=$1
tst=$2
datapath=$3
out=$4
end=$5

##change working dir
pushd main

echo ------------------
echo "Test OCLM"
echo ------------------

for fold in $(seq 1 $end)
do
  machines=machines_${fold}
  machines=/Users/dudy/CSLU/bci/5th_year/letters/evaluate/new_oclm/machines
  # rm logger if found
  export LD_LIBRARY_PATH=/usr/local/lib/fst
  python test.py --test ${datapath}/${fold}${tst} --eeg eeg_data/EEGEvidence.txt-high --nbest $nbest --machines ${machines} --output ${out}/${fold}_${nbest} --fold ${fold}
done

