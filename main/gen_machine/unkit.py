import sys

def prefix_print(datafile, wrd_lst):
  vocab = []
  for word in open(wrd_lst, 'r').readlines():
    vocab.append(word.strip())
  vocab = set(vocab)
  for g, line in enumerate(open(datafile, 'r').readlines()):
    line = line.strip()
    line = line.split()
    new_line = []
    for word in line:
      # ensure word[i] is valid else continue
      if word in vocab:
        new_line.append(word)
      else:
        new_line.append("<unk>")
    print " ".join(new_line)

if __name__ == "__main__":    
  prefix_print(sys.argv[1], sys.argv[2])
    

