import sys

def intersect_print(unq_list, frq_list):
  vocab = []
  for word in open(unq_list, 'r').readlines():
    vocab.append(word.strip())
  vocab = set(vocab)
  for line in open(frq_list, 'r').readlines():
    line = line.strip()
    if line in vocab:
      print line

if __name__ == "__main__":    
  intersect_print(sys.argv[1], sys.argv[2])
    

