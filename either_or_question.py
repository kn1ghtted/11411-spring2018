from statics import *
import sys
sys.path.append("./utility/")
from utility import *
from const_tree import *
import string

def generate_either_or_question(root):
    NP = None
    VP = None
    # check if NP VP exists in top level
    for child in root.children[0].children:

        if child.type == "NP":
            NP = child
        elif child.type == "VP":
            VP = child

    if (NP is None) or (VP is None):
        return None

    be_verb = None
    ADJP = None
    JJ_in_ADJP = None
    ADVP = None

    # scan for BE_VERB
    for word in VP.to_string().split():
        if word in BE_VERBS:
            be_verb = word

    for child in VP.children:
        if child.type == "ADJP":
            ADJP = child
            for cc in ADJP.children:
                if cc.type == "JJ":
                    JJ_in_ADJP = cc
        if child.type == "ADVP":
            ADVP = child

    # ask question for [be_verb] + [ADJP]
    print "ADJP:", ADJP, " be_verb:", be_verb, " JJ:", JJ_in_ADJP

    if (ADJP is not None) and (be_verb is not None) and (JJ_in_ADJP is not None):
        # get antonym of JJ
        antonyms = []
        for S in wn.synsets(JJ_in_ADJP.to_string()):
            print "Synset:", S
            # if Synset is adjective or a satellite-adj
            if S.pos() in ["a", "s"]:
                for lemma in S.lemmas():
                    print "lemma:", lemma
                    # if S has antonym
                    if lemma.antonyms():
                        antonyms += [ant.name() for ant in lemma.antonyms()]

        print "antonyms:", antonyms

        tokens = root.to_string().split()
        tokens_without_be_verb = list(filter(lambda x: x not in BE_VERBS, tokens))



        def F(word, A):
            print "word:", word
            word = word.lower()
            if word == JJ_in_ADJP.to_string():
                word += " or " + A[0]
                print "returning:", word
                return word
            print "returning:", word
            return word

        tokens_with_antonym = [F(token, antonyms) for token in tokens_without_be_verb]

        final_tokens = [string.capitalize(be_verb)] + tokens_with_antonym[:-1] + ["?"]

        return " ".join(final_tokens)














