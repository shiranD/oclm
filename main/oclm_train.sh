#!/bin/bash

set -x
set -e

ch_sym=$1
trn=$2
datapath=$3
out=$4
end=$5

##change working dir
pushd main

## special symbol labels
sigma=65535
phi=65536
rho=65537

for fold in $(seq 1 $end)
do
  machines=machines_${fold}
  mkdir -p ${machines}
  # LTR_DIST
  echo ------------------
  echo "LTR_DIST"
  echo ------------------
  gen_machine/./ltr_dist_gen.sh ${ch_sym} $sigma ${machines}
  
  # CH_AFTER
  echo ------------------
  echo "CH_AFTER"
  echo ------------------
  gen_machine/./ch_after_gen.sh ${ch_sym} $sigma ${machines}
  
  # CH_BEFORE
  echo ------------------
  echo "CH_BEFORE"
  echo ------------------
  gen_machine/./ch_before_gen.sh ${ch_sym} ${machines}
  
  # LENGTH MACHINE
  echo ------------------
  echo "LENGTH MACHINE"
  echo ------------------
  gen_machine/./length_machine_gen.sh ${ch_sym} $sigma ${machines}

 # process train files (discard words with a <5 counts and ensure compatibility with word symbol system) 
 # generate wd_sym
  cat ${datapath}/${fold}${trn} | tr -d ' \t\r' | sed 's/#/ /g' | tr -s '[[:punct:][:space:]]' '\n' | sort | uniq -c | sort -nr > gen_machine/wrd_frq
  cat ${datapath}/${fold}${trn} | tr -d ' \t\r' | sed 's/#/ /g' | tr -s '[[:punct:][:space:]]' '\n' | sort > gen_machine/wrd_frq2
  cat gen_machine/wrd_frq | grep -n -m1 '^\s*4\s' | egrep -o '^[^:]+' > ln_num
  num=$(cat ln_num)
  rm ln_num
  # check
  cat gen_machine/wrd_frq | head -n$(($num-1)) | awk '{print $2}' | sort > gen_machine/pre_iv_wrd_list
  # given the uniq list extract the freq list
  python gen_machine/intersect.py gen_machine/pre_iv_wrd_list gen_machine/wrd_frq2 > gen_machine/iv_wrd_list
  cat gen_machine/wrd_frq | tail -n +$num | awk '{print $2}' | sort > gen_machine/ov_wrd_list
  python gen_machine/wrd_sym_gen.py gen_machine/pre_iv_wrd_list sigma=65535 phi=65536 rho=65537 unk=65538> wd_sym.txt
#  exit
  wd_sym=wd_sym.txt  

  # IN VOCAB LEX
  echo ------------------
  echo "IN VOCAB LEX"
  echo ------------------
  cat gen_machine/iv_wrd_list | python gen_machine/mklex_nophi.py > iv_lex.txt
  gen_machine/./ltr2wrd_gen.sh iv_lex.txt ${wd_sym} ${ch_sym} iiv_lex ${machines} 

  # OUT VOCAB LEX
  echo ------------------
  echo "OUT OF VOCAB LEX"
  echo ------------------
  python gen_machine/prefixCorp.py gen_machine/ov_wrd_list > ov_lex.txt
  gen_machine/./ltr2wrd_unk.sh ov_lex.txt ${wd_sym} ${ch_sym} unk_ltr_lm_trans_lex ${machines} 

  # TRAILING LEX
  echo ------------------
  echo "TRAILING LEX"
  echo ------------------
  cat gen_machine/iv_wrd_list | python gen_machine/mklex_trailing.py > trail.txt
  gen_machine/./ltr2wrd_gen.sh trail.txt ${wd_sym} ${ch_sym} trailing_lex ${machines} 

  # REFINER
  echo ------------------
  echo "REFINER"
  echo ------------------
  gen_machine/./ref_gen.sh ${wd_sym} $sigma ${machines}

  # WORD SIGMA
  echo ------------------
  echo "WORD SIGMA"
  echo ------------------
  gen_machine/./wrd_sg_gen.sh ${wd_sym} $sigma ${machines}


  # WORD_LM
  echo ------------------
  echo "WORD_LM"
  echo ------------------
  cat ${datapath}/${fold}${trn} | tr -d ' \t\r' | sed 's/#/ /g' > trn_sent 
  # replace all unk in gen_machine/ov_wrd_list w/ unk
  python gen_machine/unkit.py trn_sent gen_machine/iv_wrd_list > n_trn_sent
  python gen_machine/wprefixCorp.py n_trn_sent > prf.txt
  gen_machine/./wrd_lm_gen.sh prf.txt ${wd_sym} ${machines}
  rm prf.txt
  rm trn_sent
  rm n_trn_sent

  echo ------------------
  echo "LTR_LM"
  echo ------------------
  # LTR_LM
  python gen_machine/prefixCorp.py gen_machine/iv_wrd_list > ${datapath}/${fold}_corpus.txt
  gen_machine/./ch_lm_gen.sh ${datapath}/${fold}_corpus.txt ${ch_sym} ${machines}

  echo ------------------
  echo "SPELLOUT"
  echo ------------------
  # SPELLOUT

  export LD_LIBRARY_PATH=/usr/local/lib/fst
  python gen_machine/spellout.py gen_machine/pre_iv_wrd_list machines/iiv_lex.fst
  mv spellout.fst ${machines}
  rm gen_machine/pre_iv_wrd_list
  rm gen_machine/iv_wrd_list
  rm gen_machine/ov_wrd_list
  rm gen_machine/wrd_frq
  rm gen_machine/wrd_frq2
  rm trail.txt
  rm iv_lex.txt
  rm ${wd_sym}
done

