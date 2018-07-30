import argparse
import sys
import random
import re
import string

# shuffle sentneces
# split to N folds
# write N folds on a word level

random.seed(10)

dig = re.compile('\d')
def contains_dig(string):
  return bool(dig.search(string))

def split(args):
  """
  This script split the sentence sorpus to N folds
  of the way split
  N > 3
  """
  # filter sentences that are oov w.r.t. the embedding
  corpus = []
  with open(args.fdata, encoding = "ISO-8859-1") as f:
    for line in f:
      line = line.strip()
      sen = line.lower()
      sen = ''.join(x for x in sen if x not in string.punctuation)
      sen = ''.join(i for i in sen if (ord(i)<123 and ord(i)>31))
      if contains_dig(sen):
        continue
      sen = sen.split()
      sen = "#".join(sen)
      corpus.append(sen)

  # break into folds
  for itr in range(args.folds):
    # an outer loop makes it N fold sets
    ftrain = open(args.odir+str(itr)+args.train, "w")
    ftest = open(args.odir+str(itr)+args.test, "w")

    for fold in range(args.folds):
      test = corpus[fold::args.folds]
      for tst in test:
        ftest.write(tst)
        ftest.write("\n")
      for i in range(args.folds):
        if i!=fold:
          shard = corpus[i::args.folds]
          for sentence in shard:
            sentence = " ".join(list(sentence))  
            ftrain.write(sentence)
            ftrain.write("\n")
         
    ftest.close()
    ftrain.close()

if __name__ == "__main__":

  parser = argparse.ArgumentParser(
      description='Split Data')
  parser.add_argument('--train', type=str, help='train file name')
  parser.add_argument('--test', type=str, help='test file name')
  parser.add_argument('--fdata', type=str, help='corpus of sentences file name')
  parser.add_argument('--odir', type=str, help='output dir')
  parser.add_argument('--folds', type=int, help='folds')
  args = parser.parse_args()
  split(args)
  
