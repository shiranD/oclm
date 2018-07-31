from __future__ import division
import pywrapfst as fst
from ebitweight import BitWeight
from oclm_c import oclm
import math

class server:
    '''
    a class to generate
    OCLM-based priors and 
    provide word predictions
    '''
    def __init__(self, machine_path):
        # load pre-processd fst machines
        self.lm = oclm(machine_path)
 
    def init(self, nbest):
        # init
        self.nbest = nbest
        self.lm.init()

    def reset(self):
        # init
        self.lm.init()

    def state_update(self, evidence, return_mode):
        '''
        Online Context Language Model
        '''
        for eeg_timestep in self.__process_evidence(evidence):
            history_chars = self.lm.separate_sausage(self.lm.history_fst, self.lm.ch_before_last_space_fst)
            trailing_chars = self.lm.separate_sausage(self.lm.history_fst, self.lm.ch_after_last_space_fst)
    
            word_lattice = fst.compose(history_chars, self.lm.ltr2wrd)
            word_lattice.project(project_output=True).rmepsilon()
            word_lattice = fst.determinize(word_lattice)
            word_lattice.minimize().topsort()
            if word_lattice.num_states() == 0:
                word_lattice = self.lm.create_empty_fst(self.lm.wd_syms, self.lm.wd_syms)
    
            trailing_chars_sigma = self.lm.add_char_selfloop(trailing_chars, self.lm.ch_syms)
            trailing_chars_sigma.arcsort(sort_type="olabel")
            current_words = fst.compose(trailing_chars_sigma, self.lm.tr_ltr2wrd)
            current_words.project(project_output=True).rmepsilon()
            current_words = fst.determinize(current_words)
            current_words.minimize().topsort()
            word_seq = word_lattice.copy().concat(current_words).rmepsilon()
            topk_wds = []
            topk = self.lm.topk_choice(word_seq)
    
            united_LM = self.lm.combine_ch_lm(topk, topk_wds)
            self.lm.append_eeg_evidence(eeg_timestep)
            
            priors = self.lm.next_char_dist(trailing_chars, united_LM)

        if return_mode == 'letter': 
            return sorted(priors, key=lambda x: x[1])
        else: 
            topk_wds = self.lm.get_topk_words(topk)
            return sorted(priors, key=lambda x: x[1]), topk_wds
 
    def __process_evidence(self, eeg):
        '''
        grab nbest and normalize
        '''
        for timestep in eeg:
            nbest_eeg_dist = timestep[:self.nbest]
            # Normalizes the EEG evidence.
            tmp_dst = [math.e**(pr) for _,pr in nbest_eeg_dist]
            total = sum(tmp_dst)
            norm_tmp_dst = [-math.log(pr / total) for pr in tmp_dst]
            yield zip([ch for ch,_ in nbest_eeg_dist], norm_tmp_dst)
