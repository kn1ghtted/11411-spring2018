import string
from utility import *
from statics import *
from pattern.en import lemma
import string
from nltk.corpus import wordnet as wn


"""
Functions and constants for ask, generating binary questions
"""

# define answer strings
YES_ANSWER = "Yes."
NO_ANSWER = "No."


def answer_binary_by_comparison(question, sentence):
    """
    Basic idea: for important words in the question, check if it or its synonyms
    exist in the original sentence.
    List of important words' tags:
        numbers: CD
        nouns: NN, NNS, NNP, NNPS
        verbs: VB, VBD, VBG, VBN, VBP, VBZ
        misc: FW
        adjectives: JJ, JJR, JJS
        adverbs: RB, RBR, RBS
    Policies:
        number: check if it or its synonym exists in the original sentence
        noun:
            NN and NNS: check if it or its synonym exists in the original sentence
            NNP and NNPS: check if it exists in the original sentence
        verbs: check if it or its synonym exists in the original sentence
        misc: check if it exists in the original sentence
        adjectives and adverbs:
            check if it exists in the original sentence:
                if yes:
                    continue
                if no:
                    check if its antonyms exist in the original sentence:
    """

    def _check_word_existence(word, word_sets):
        return word.lower() in word_sets or wn.morphy(word) in word_sets or lemma(
            word) in word_sets

    def _check_synonyms_existence(word, word_sets, wn_pos):
        for synsets in wn.synsets(word.lower(), pos=wn_pos):
            for name in synsets.lemma_names():
                if name in word_sets or wn.morphy(name) in word_sets or lemma(
                        name) in word_sets:
                    return True
        return False

    def _check_antonyms_existence(word, word_sets, wn_pos):
        for le in wn.lemmas(word, pos=wn_pos):
            for antonym in le.antonyms():
                name = antonym.name()
                if name in word_sets or wn.morphy(name) in word_sets or lemma(
                        name) in word_sets:
                    return True
        return False

    question = question.translate(None, string.punctuation)
    sentence = sentence.translate(None, string.punctuation)
    word_sets = set()
    for word in sentence.lower().split():
        word_sets.add(word)
        # also adds the word's base form to the sets
        word_sets.add(wn.morphy(word))
        word_sets.add(lemma(word))
    # remove None in the sets
    word_sets = word_sets - {None}
    for word, tag in nltk.pos_tag(nltk.word_tokenize(question))[1:]:
        word = word.lower()
        if tag == 'CD':
            if not _check_word_existence(word, word_sets) and \
                    not _check_synonyms_existence(word, word_sets, None):
                return NO_ANSWER
        elif tag == 'NN' or tag == 'NNS':
            if not _check_word_existence(word, word_sets) and \
                    not _check_synonyms_existence(word, word_sets, wn.NOUN):
                return NO_ANSWER
        elif tag == 'NNP' or tag == 'NNPS':
            if not _check_word_existence(word, word_sets):
                return NO_ANSWER
        elif tag[:2] == 'VB':
            if not _check_word_existence(word, word_sets) and \
                    not _check_synonyms_existence(word, word_sets, wn.VERB):
                return NO_ANSWER
        elif tag[:2] == 'JJ':
            if not _check_word_existence(word, word_sets) and \
                    not _check_synonyms_existence(word, word_sets, wn.ADJ) and \
                    _check_antonyms_existence(word, word_sets, wn.ADJ):
                return NO_ANSWER
        elif tag[:2] == 'RB':
            if not _check_word_existence(word, word_sets) and \
                    not _check_synonyms_existence(word, word_sets, wn.ADV) and \
                    _check_antonyms_existence(word, word_sets, wn.ADV):
                return NO_ANSWER
    return YES_ANSWER

def ask_binary_question(node, parent_NP):
    """
    # Analyze structure of the VP node
    # Split into two cases:
    # 1) VB{P,B,D,Z,N} + ... + VP + ... (am eating a sandwich)
    # 2) VB{P,B,D,Z,N} + ... + NP + ... (ate a sandwich)
    :param node: current VP node
    :param parent_NP: parent NP node
    :return: generated binary question
    """
    question = ""
    VP = None
    VBX = None # for auxiliary verb
    for child in node.children:
        if (child.type == "VP"):
            VP = child
        if (child.type.startswith("VB")):
            VBX = child
        # Discard sentence with conjunction structure
        if (child.type == "CC"):
            return None

    parent_NP_string = lowercase_if_needed(parent_NP)

    # discard sentence with no VBX
    if VBX == None:
        return

    # has auxiliary verb
    if (VP != None):
        question += string.capitalize(VBX.to_string())
        question += " " + parent_NP_string + " " + VP.to_string() + "?"
    # no auxiliary verb
    else:
        if VBX.type not in VERB_TYPE_AUX_VERB_MAPPING:
            return None

        # get vp_without_verb
        children_except_VBX = list(filter(lambda child: (not child.type.startswith("VB")), node.children))
        vp_without_verb = " ".join(list(map(lambda child: child.to_string(), children_except_VBX)))

        if VBX.to_string() in BE_VERBS:
            question += string.capitalize(VBX.to_string()) + ' ' + parent_NP_string + ' ' + vp_without_verb + '?'
        else:
            question += VERB_TYPE_AUX_VERB_MAPPING[VBX.type]
            question += ' ' + parent_NP_string + ' ' + lemma(VBX.to_string()) + ' ' + vp_without_verb + '?'
    return question