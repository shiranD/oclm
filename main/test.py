import argparse
from eeg_data.eeg_utils import simulate_eeg 
import oclm
import json
import io

def process_prior(dist, sym):

  dist = sorted(dist, key=lambda x:x[1])
  for k, (char, prob) in enumerate(dist):
    if char==sym:
      pp = prob
      rank = k+1

  return rank, pp

def test(args):

  return_mode = 'letter'
  simulator = simulate_eeg(args.eeg)
  jsonf = args.output + str(args.fold) + ".json"
  with io.open(jsonf, "w", encoding='utf8') as outfile: 
    for sent in open(args.test).readlines():
      sent = sent.strip()
      lm = oclm.server(args.machines)
      lm.init(args.nbest)
      ranks = []
      acc1 = 0
      acc10 = 0
      ppx = []
      for letter in sent:
        # simulate input
        evidence = simulator.simulate(letter)
        # get priors
        priors = lm.state_update(evidence, return_mode)
        # here is your place to store statistics you care about
        # over stroing the entire prediction which may not 
        # be memory efficient (MRR, R@1, R@10)
        rank, pp = process_prior(priors, letter)
        # R of MRR
        # Notice: here MRR is stroed just by storing the target ranks
        ranks.append(rank)
        # PPX
        ppx.append(pp)
        if rank < 11:
          # ACC@10
          acc10+=1
          if rank == 1:
            # ACC@1
            acc1+=1
      data = {'ranks': ranks, 'acc1': acc1, 'acc10': acc10, 'ppx': ppx}
      str_ = json.dumps(data, indent =4 , separators = (',', ': '), ensure_ascii=True)
      outfile.write(unicode(str_))
      outfile.flush()

if __name__ == "__main__":

  parser = argparse.ArgumentParser(
      description='Test OCLM')
  parser.add_argument('--machines', type=str, help='path to FST machines')
  parser.add_argument('--test', type=str, help='path to test sentences')
  parser.add_argument('--nbest', type=int, help='nbest')
  parser.add_argument('--eeg', type=str, help='path to EEG simulations')
  parser.add_argument('--output', type=str, help='path to json folder')
  parser.add_argument('--fold', type=int, help='fold number')
  parser.add_argument('--demo', type=bool, help='demo on')
  args = parser.parse_args()
  if args.demo:
    demo(args)
  else:
    test(args)
