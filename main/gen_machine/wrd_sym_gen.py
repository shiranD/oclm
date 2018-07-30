import sys

def make_wrd_symbols(wlist, uniqlist):
  print "<epsilon>\t0"
  for i, word in enumerate(open(wlist, 'r').readlines()):
    word = word.strip()
    print word,"\t",str(i+1)
  for uniq in uniqlist:
    sym, num = uniq.split("=")
    sym = "<"+sym+">"
    print sym,"\t",num
      
if __name__ == '__main__':
  wrd_list = sys.argv[1]
  sigma = sys.argv[2]
  rho = sys.argv[3]
  phi = sys.argv[4]
  unk = sys.argv[5]
  make_wrd_symbols(wrd_list, [sigma, rho, phi, unk])
