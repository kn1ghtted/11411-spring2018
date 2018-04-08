import nltk
import re

from nltk.corpus import wordnet as wn

def text2sentences(text):
    ret = list()
    # remove non-ascii characters
    text = re.sub(r'[^\x00-\x7f]',r'', text)
    for sentence in nltk.sent_tokenize(text):
        ret += re.split('\n+', sentence)
    return ret

# get the lexname/supersense of the word
# E.G.: "student" -> noun.person

def get_word_supersense(w):
    synsets = wn.synsets(w)
    if len(synsets) == 0:
        raise Exception("No supersense found!")
    return synsets[0].lexname()