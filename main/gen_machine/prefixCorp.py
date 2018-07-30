import sys

def prefix_print(datafile):
    
    for g, line in enumerate(datafile.readlines()):
        line = list(line.strip())
        line = " ".join(line)
        for i in range(len(line)/2):
            print line[:i*2+1]
        print line+" #"
                
if __name__ == "__main__":    
    corpus = open(sys.argv[1])
    prefix_print(corpus)
    

