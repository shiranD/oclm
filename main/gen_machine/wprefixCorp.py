import sys

def prefix_print(datafile):
  for g, line in enumerate(open(datafile, 'r').readlines()):
    line = line.strip()
    line = line.split()
    for i, word in enumerate(line):
      print " ".join(line[:i+1])

if __name__ == "__main__":    
  prefix_print(sys.argv[1])
    

