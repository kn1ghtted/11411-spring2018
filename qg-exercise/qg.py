# Fixed issues
# Conjunction in VP? Discarding for now
# have as real verb or auxiliary verb? fixed in function 'analyze_vp_structure'
# NNP and NP? fixed in function "lowercase_if_needed"
# TODO
# Anaylyze what "it" refers to

from stanfordcorenlp import StanfordCoreNLP
from const_tree import const_tree
from pattern.en import lemma
import nltk
import re
import string


STANFORD_NLP_PATH = "/Users/teddyding/11411/stanford-corenlp-full-2017-06-09"
#STANFORD_NLP_PATH = "/home/lxy/stanford-corenlp-full-2017-06-09"

AUX_VERBS = {'am', 'are', 'is', 'was', 'were', 'being', 'been', 'can', \
             'could', 'dare', 'do', 'does', 'did', 'have', 'has', 'had', 'having', \
             'may', 'might', 'must', 'need', 'ought', 'shall', 'should', 'will', 'would'}
VERB_TYPE_AUX_VERB_MAPPING = {'VB': 'Do', 'VBZ': 'Does', 'VBP': 'Do', 'VBD': 'Did'}
BE_VERBS = {'am', 'is', 'are', 'were', 'was'}


def text2sentences(text):
    ret = list()
    # remove non-ascii characters
    text = re.sub(r'[^\x00-\x7f]',r'', text)
    for sentence in nltk.sent_tokenize(text):
        ret += re.split('\n+', sentence)
    return ret

# Lower case the NP in the top level, if needed (when it's not a proper noun)
def lowercase_if_needed(parent_NP):
    if parent_NP.children[0].type.startswith("NNP"):
        return parent_NP.to_string()
    if parent_NP.to_string() == "I":
        return "I"
    else:
        tokens = parent_NP.to_string_recur()
        return " ".join([tokens[0].lower()] + tokens[1:])

# Analyze structure of the VP node
# Split into two cases:
# 1) VB{P,B,D,Z,N} + ... + VP + ... (am eating a sandwich)
# 2) VB{P,B,D,Z,N} + ... + NP + ... (ate a sandwich)

def analyze_vp_structure(node, parent_NP):
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


def generate_binary_question(sentence):
    print "[INFO] Processing sentence: ", sentence
    question = ''
    parsed_string = nlp.parse(sentence)
    root = const_tree.to_const_tree(parsed_string)
    np = None
    # verb = None
    vp = None
    # vp_without_verb = None
    for child in root.children[0].children:
        if child.type == 'NP':
            np = child
            # np = child.to_string()
            # np = np[0].lower()+np[1:]
        if child.type == 'VP':
            vp = child
            # tokens = child.to_string_recur()
            # verb = tokens[0]
            # vp_without_verb = ' '.join(tokens[1:len(tokens)])
            # verb_type = child.children[0].type

    if np == None or vp == None:
        return None
    # case on VP
    return analyze_vp_structure(vp, np)
    # if verb in AUX_VERBS:
    #     question += string.capitalize(verb)
    #     question += ' ' + np + ' ' + vp_without_verb + '?'
    # else:
    #     if verb_type not in VERB_TYPE_AUX_VERB_MAPPING:
    #         return None
    #     question += VERB_TYPE_AUX_VERB_MAPPING[verb_type]
    #     question += ' ' + np + ' ' + lemma(verb) + ' ' + vp_without_verb + '?'

if __name__ == '__main__':
    input_file = 'sample_input.txt'
    with open(input_file, 'r') as f:
        text = f.read()

    sentences = text2sentences(text)

    # remove sentences not ending with '.'
    sentences = [x for x in sentences if x[-1:] is '.']

    nlp = StanfordCoreNLP(STANFORD_NLP_PATH)

    questions = list()

    for sentence in sentences:
        question = generate_binary_question(sentence)
        if question is not None:
            questions.append(question)
            print "[INFO]", question
            print '\n'

    nlp.close()