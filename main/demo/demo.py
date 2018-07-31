import argparse
from eeg_data.eeg_utils import simulate_eeg
import oclm
from print_it import histit, print_evidence

def demo(args):
    """
    Show the OCLM in action
    """
    return_mode = 'word'
    simulator = simulate_eeg(args.eeg)
    for sent in open(args.test).readlines():
        sent = sent.strip()
        lm = oclm.server(args.machines)
        lm.init(args.nbest)
        old_eeg = []
        processed_eeg = []
        old_target = ""
        for letter in sent:
            # simulate input
            evidence = simulator.simulate(letter)
            # get priors
            letters, words = lm.state_update(evidence, return_mode)
            char_sym, char_pr = map(list,zip(*letters))
            word_sym, word_pr = map(list,zip(*words))
            char_pr = [pr*100 for pr in char_pr]
            word_pr = [pr*100 for pr in word_pr]
            processed_eeg = print_evidence(old_eeg, processed_eeg, old_target)
            histit(char_pr, char_sym, word_pr, word_sym)
            print("-" * 89)
            raw_input("")
            old_target = letter
            old_eeg = evidence[0][:args.nbest]


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Demonstrate OCLM')
    parser.add_argument('--machines', type=str, help='path to FST machines')
    parser.add_argument('--test', type=str, help='path to test sentences')
    parser.add_argument('--nbest', type=int, help='nbest')
    parser.add_argument('--eeg', type=str, help='path to EEG simulations')
    args = parser.parse_args()
    demo(args)
