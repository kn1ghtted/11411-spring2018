# Fixed issues
# Conjunction in VP? Discarding for now
# have as real verb or auxiliary verb? fixed in function 'analyze_vp_structure'
# NNP and NP? fixed in function "lowercase_if_needed"
# Anaylyze what "it" refers to

import sys
sys.path.append('../utility/')

from stanfordcorenlp import StanfordCoreNLP
from const_tree import const_tree
from pattern.en import lemma

import string
from nltk.tag.stanford import StanfordNERTagger
from nltk.tag.stanford import CoreNLPNERTagger
from nltk.parse.corenlp import CoreNLPParser
from utility import *


# STANFORD_NLP_PATH = "/Users/teddyding/11411/stanford-corenlp-full-2017-06-09"
#STANFORD_NLP_PATH = "/home/lxy/stanford-corenlp-full-2017-06-09"
STANFORD_NLP_PATH = "/Users/anitawang/Desktop/11411/NLP/stanford-corenlp-full-2018-02-27"

AUX_VERBS = {'am', 'are', 'is', 'was', 'were', 'being', 'been', 'can', \
             'could', 'dare', 'do', 'does', 'did', 'have', 'has', 'had', 'having', \
             'may', 'might', 'must', 'need', 'ought', 'shall', 'should', 'will', 'would'}
VERB_TYPE_AUX_VERB_MAPPING = {'VB': 'Do', 'VBZ': 'Does', 'VBP': 'Do', 'VBD': 'Did'}
BE_VERBS = {'am', 'is', 'are', 'were', 'was'}
st = StanfordNERTagger('/Users/anitawang/Desktop/11411/NLP/stanford-ner-2018-02-27/classifiers/english.all.3class.distsim.crf.ser.gz',
           '/Users/anitawang/Desktop/11411/NLP/stanford-ner-2018-02-27/stanford-ner.jar')
ner = CoreNLPNERTagger(url='http://nlp01.lti.cs.cmu.edu:9000/')





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

def get_supersense(np_string):
    result = None
    for word in np_string.split(" "):
        try:
            labelSet = get_word_supersenses(word)
        except:
            continue
        # if is person
        if "noun.person" in labelSet:
            result = "Who"
        elif "noun.artifact" in labelSet:
            result = "What"
        else:
            result = None
        return result

    
# takes in a NP node
def getWhWord(np):
    result = None
    for child in np.children:
        childTag = child.type
        if childTag == "PRP" and str.lower(child.word) != "it":
            if result != None and result != "Who": return None
            result = "Who"
    NP_string = const_tree.to_string(np)
    NER_result = ner.tag(NP_string.split())
    for (word, tag) in NER_result:
        if tag == "PERSON":
            if result != None and result != "Who": return None
            result = "Who"
        elif tag == "TIME":
            if result != None and result != "TIME": return None
            result == "When"
        elif tag == "DATE":
            if result != None and result != "DATE": return None
            result == "When"
        elif tag == "MONEY":
            if result != None and result != "MONEY": return None
            result = "How much"
        elif tag == "GPE":
            if result != None and result != "GPE": return None
            result = "Where"
    if not result:
        result = get_supersense(NP_string)

    return result


def generate_wh_question(vp,np):
    question = ""
    hasPerson = False
    WH = getWhWord(np)
    if not WH:
        return None
    question +=  WH + " "
    rest = const_tree.to_string(vp)
    question += rest
    question += "?"
    return question



def generate_binary_question(sentence, wh):
    print "[Sentence] ", sentence
    question = ''
    parsed_string = str(next(nlpParser.raw_parse(sentence)))
    root = const_tree.to_const_tree(parsed_string)
    np = None
    vp = None
    for child in root.children[0].children:
        if child.type == 'NP':
            np = child
        if child.type == 'VP':
            vp = child

    if np == None or vp == None:
        return None
    # case on VP
    return generate_wh_question(vp, np)




if __name__ == '__main__':
    input_file = 'sample_input.txt'
    with open(input_file, 'r') as f:
        text = f.read()

    sentences = text2sentences(text)

    # remove sentences not ending with '.'

    sentences = [x for x in sentences if x[-1:] is '.']

    nlpParser = CoreNLPParser(url='http://nlp01.lti.cs.cmu.edu:9000/')
    questions = list()
    

    for sentence in sentences:
        question = generate_binary_question(sentence,True)
        if question is not None:
            questions.append(question)
            print "[Question] ", question
            print '\n'


    # sentence = "I ate an sandwich"
    # print(generate_binary_question(sentence, True))
    # nltk.tag.corenlp.CoreNLPNERTagger
    # print nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize("I work in China yesterday.")))
    # print st.tag("I work in China yesterday.".split())
    # print parser.ner("I work in China yesterday")
