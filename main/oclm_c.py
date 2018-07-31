from __future__ import division
import pywrapfst as fst
import math
from ebitweight import BitWeight
import specializer

class oclm:
    def __init__(self, machines):
        #print 'loading predefined fsts...'
        self.spell = fst.Fst.read(machines + "/spellout.fst")
        self.prefix_lm = fst.Fst.read(machines + "/ltr_lm.fst")
        self.refiner = fst.Fst.read(machines + "/refiner.fst")
        self.lm = fst.Fst.read(machines + "/word_lm.fst")
        self.sig_mcn = fst.Fst.read(machines + "/sigma_machine_words.fst")
        self.ch_after_last_space_fst = fst.Fst.read(machines + "/ch_after_last_space.sigma.fst")
        self.ch_before_last_space_fst = fst.Fst.read(machines + "/ch_before_last_space.fst")
        self.length_fst = fst.Fst.read(machines + "/length_machine.sigma.fst")
        self.ltr_dist = fst.Fst.read(machines + "/ltr_dist.sigma.fst")
        #self.ch_syms = fst.SymbolTable.read_text(machines + "/ch_syms")
        self.ch_syms = self.spell.output_symbols()
        self.wd_syms = self.lm.input_symbols()
        self.SIGMA = self.wd_syms.find('<sigma>')
        self.factor = 0.5
        # each element consists of the word lattice, trailing characters and the number.
        self.prefix_words = [
                [self.create_empty_fst(self.wd_syms, self.wd_syms),
                 self.create_empty_fst(self.ch_syms, self.ch_syms),
                 0]]
        # Creates the history sausage.

        self.unk_lex = fst.Fst.read(machines + "/unk_ltr_lm_trans_lex.fst")
        self.no_phi_lex = fst.Fst.read(machines + "/iiv_lex.fst")
        self.ltr2wrd = self.__weighted_union(self.unk_lex, self.no_phi_lex, 0.5, 0.5).closure().arcsort()
        self.tr_ltr2wrd = fst.Fst.read(machines + "/trailing_lex.fst")
    
    def init(self):
        '''
        create history fst
        '''

        self.history_fst = self.create_empty_fst(self.ch_syms, self.ch_syms)

    def add_char_selfloop(self, ifst, symTbl):
        ofst = ifst.copy()
        f = fst.Fst()
        f.set_input_symbols(symTbl)
        f.set_output_symbols(symTbl)
        f.add_state()
        f.set_start(0)
        for code, ch in symTbl:
            if ch.startswith("<") or ch == "#":
                continue
            #f.add_arc(0, fst.Arc(code, code, math.log(26), 0))
            f.add_arc(0, fst.Arc(code, code, None, 0))
        f.add_state()
        space_code = symTbl.find("#")
        f.add_arc(0, fst.Arc(space_code, space_code, None, 1))
        f.set_final(1)
        ofst.concat(f)
        #ofst.rmepsilon()
        return ofst

    def create_empty_fst(self, input_sym, output_sym):
        '''
        Create an empty fst (only one state being final).
        '''
        f = fst.Fst()
        f.set_input_symbols(input_sym)
        f.set_output_symbols(output_sym)
        f.add_state()
        f.set_start(0)
        f.set_final(0)
        return f

    def normalize(self, anfst):
        '''
        produce a normalized fst
        '''
        # possibly there's a shorter way
        # that keeps all in fst land
        dist = []
        labels = []
        syms = anfst.input_symbols()
        state = anfst.start()
        flag = 0
        for arc in anfst.arcs(state):
            label = syms.find(arc.ilabel)
            pr = float(arc.weight)
            dist.append(BitWeight(pr)) # ebitweight gets -log(pr) only
            labels.append(label)
            if not flag: # init sum with fist value
                sum_value = BitWeight(pr)
                flag = 1
        # normalize distribution
        for value in dist[1:]:
            sum_value+=value # will sum in log domain (log-add)
        norm_dist = [(prob/sum_value).loge() for prob in dist]
        del anfst
        # construct a norm fst
        output = fst.Fst()
        output.set_input_symbols(syms)
        output.set_output_symbols(syms)
        output.add_state()
        output.add_state()
        for (pr, label) in zip(norm_dist,labels):
            code = syms.find(label)
            output.add_arc(0, fst.Arc(code, code, pr, 1))
        output.set_start(0)
        output.set_final(1)
        return output

    def wrd2ltr(self, fstout):
        # if there are normalization methods in fst land..
        norm_fst = self.normalize(fstout)
        letter = fst.compose(norm_fst, self.spell)
        letter.push(to_final=False)
        letter.project(project_output=True)
        letter.rmepsilon()
        letter = fst.determinize(letter)
        for state in letter.states():
            if state==0:
                continue
            letter.set_final(state)
        
        return letter

    def __weighted_union(self, left, right, left_prob, right_prob):
        '''
        Union the FSTs left, right with a weight.
        '''
        # left hand side part.
        left_w = -math.log(left_prob)
        lhs = fst.Fst()
        lhs.set_input_symbols(left.input_symbols())
        lhs.set_output_symbols(left.output_symbols())
        lhs.add_state()
        lhs.set_start(0)
        lhs.add_state()
        lhs.add_arc(0, fst.Arc(0, 0, left_w, 1))
        lhs.set_final(1)
        lhs.concat(left)

        # prefix part.
        right_w = -math.log(right_prob)
        rhs = fst.Fst()
        rhs.set_input_symbols(right.input_symbols())
        rhs.set_output_symbols(right.output_symbols())
        rhs.add_state()
        rhs.set_start(0)
        rhs.add_state()
        rhs.add_arc(0, fst.Arc(0, 0, right_w, 1))
        rhs.set_final(1)
        rhs.concat(right)

        lhs.union(rhs)
        return lhs


    def combine_ch_lm(self, topk_fst, topk_wds=[]):
        '''
        Combine the spellout machine with prefix character
        language model, using the factor:
        factor * top_k + (1 - factor) * prefix_lm
        '''
        if topk_fst is None or topk_fst.num_states() == 0:
            return self.prefix_lm
        ltr_topk = self.spellout(topk_fst, topk_wds)
        return self.__weighted_union(self.prefix_lm, ltr_topk, self.factor, 1-self.factor)

    def get_topk_words(self, ifst):
        '''
        Returns a list of topk words with normalized weights and sorted
        by descending order.
        INPUT: ifst: an fst containing the topk choices.
        '''
        dist = []
        labels = []
        syms = ifst.input_symbols()
        state = ifst.start()
        for arc in ifst.arcs(state):
            label = syms.find(arc.ilabel)
            pr = float(arc.weight)
            dist.append(BitWeight(pr)) # ebitweight gets -log(pr) only
            labels.append(label)
        sum_value = sum(dist, BitWeight(1e6))
        norm_dist = [(prob/sum_value).real() for prob in dist]
        return sorted(zip(labels, norm_dist), key=lambda x:-x[1])


    def topk_choice(self, word_sequence, topk_wds=None):
        '''
        extracts the topk choices of
        lm given a word history (lattice)
        input: lm.fst and sentence string
        output: topk words to complete the lattice
        '''

        # generate sentence fst
        fstout = fst.intersect(word_sequence, self.lm)
        fst_det = fst.determinize(fstout)
        fst_p = fst.push(fst_det, push_weights=True, to_final=True)
        fst_p.rmepsilon()
        fst_rm = fst.determinize(fst_p)
        short = fst.shortestpath(fst_rm, nshortest=10)
        short_det = fst.determinize(short)
        short_det.rmepsilon()
        two_state = fst.compose(short_det, self.refiner)
        output = two_state.project(project_output=True)
        output.rmepsilon()
        output = fst.determinize(output)
        output.minimize()
        if topk_wds is not None:  # Needs to distinguish None and []
            topk_wds.extend(self.get_topk_words(output))
        return output

    def spellout(self, ifst, topk_wds=None):
        '''
        Spells out all the words in the ifst.
        '''
        if ifst is None:
            return None
        ifst.rmepsilon()
        ofst = fst.determinize(ifst)
        ofst.minimize()
        if topk_wds is not None:
            topk_wds.extend(self.get_topk_words(ofst))
        return self.wrd2ltr(ofst)

    def add_sigma(self, fst_machine):
        fst_machine.concat(self.sig_mcn)
        fst_machine.rmepsilon()
        fst_machine.arcsort(sort_type="olabel")
        output = specializer.sigma(fst_machine, self.SIGMA, "always").get()
        return output

    def word_sequence_history(self, eeg_saus):
        '''
        generate a probable word
        sequence given the EEG samples
        by intersecting it with word
        language model
        '''

        word_seq = fst.compose(eeg_saus, self.ltr2wrd)
        fst.push(word_seq, push_weights=True, to_final=True)
        word_seq.project(project_output=True)
        word_seq.rmepsilon()
        return word_seq
        # the motivation to have a function is to
        # free the memory from ltr2wrd once the
        # intersection is done

    def separate_sausage(self, sausage, helper_fst):
        '''
        Separates history sausage based on the last space. The direction
        (before/after) depends on the helper fst passed in.
        '''
        chars = fst.compose(sausage, helper_fst)
        chars.project(True)
        chars.rmepsilon()
        chars = fst.determinize(chars)
        chars.minimize().topsort()
        return chars

    def restrict_chars_length(self, trailing_chars):
        '''
        Restrict the length of trailing characters to avoid complex computation.
        The exact number of length depending on the implementation of fst.
        '''
        restricted_length = fst.compose(trailing_chars, self.length_fst)
        restricted_length.project(project_output=True)
        restricted_length.rmepsilon()
        restricted_length = fst.determinize(restricted_length)
        restricted_length.minimize()
        return restricted_length

    def concat_alphabet(self, ifst):
        '''
        Concatenate all characters in the alphabet to the end of a given fst.
        '''
        ofst = ifst.copy()
        sigma = fst.Fst()
        sigma.set_input_symbols(ofst.input_symbols())
        sigma.set_output_symbols(ofst.output_symbols())
        sigma.add_state()
        sigma.set_start(0)
        for code, ch in ofst.input_symbols():
            if ch.startswith("<"):  # Don't include special arcs in sigma machine.
                continue
            sigma.add_arc(0, fst.Arc(code, code, None, 1))
        sigma.add_state()
        sigma.set_final(1)
        ofst.concat(sigma)
        ofst.rmepsilon()
        return ofst

    def next_char_dist(self, history, char_lm):
        '''
        Get the distribution of next character.
        '''
        history = self.concat_alphabet(history)
        history.arcsort(sort_type="olabel")
        output = fst.intersect(history, char_lm)
        output.rmepsilon()
        output = fst.determinize(output)
        output.minimize()

        # reads an fst to combine the weights of the next character.
        last_ltr = fst.compose(output, self.ltr_dist)
        last_ltr.project(True)
        last_ltr.push(to_final=True)
        last_ltr.rmepsilon()
        last_ltr = fst.determinize(last_ltr)
        last_ltr.minimize()

        # Extracts priors. Although it's a two-state machine, we have the
        # generic traverse procedure here just in case.
        prev_stateid = curr_stateid = None
        for state in last_ltr.states():
            if not curr_stateid is None:
                prev_stateid = curr_stateid
            curr_stateid = state
        priors = []
        syms = last_ltr.input_symbols()
        for arc in last_ltr.arcs(prev_stateid):
            ch = syms.find(arc.ilabel)
            w = float(arc.weight)
            if len(ch) == 1:
                priors.append((ch, w))

        # Sorts the prior by the probability and normalize it.
        priors = sorted(priors, key=lambda prior: prior[1])
        priors_vals = [BitWeight(prob) for _,prob in priors]
        total = sum(priors_vals, BitWeight(1e6))
        norm_priors = [(prob / total).loge() for prob in priors_vals]
        return zip([ch for ch,_ in priors], norm_priors)

    def append_eeg_evidence(self, ch_dist):
        new_ch = fst.Fst()
        new_ch.set_input_symbols(self.ch_syms)
        new_ch.set_output_symbols(self.ch_syms)
        new_ch.add_state()
        new_ch.set_start(0)
        new_ch.add_state()
        new_ch.set_final(1)
        for ch, pr in ch_dist:
            code = self.ch_syms.find(ch)
            new_ch.add_arc(0, fst.Arc(code, code, pr, 1))
        new_ch.arcsort(sort_type="olabel")
        self.history_fst.concat(new_ch).rmepsilon()
        #print self.history_fst
