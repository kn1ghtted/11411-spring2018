#!/usr/bin/env python

# Fixed issues
# Conjunction in VP? Discarding for now
# have as real verb or auxiliary verb? fixed in function 'analyze_vp_structure'
# NNP and NP? fixed in function "lowercase_if_needed"
# Anaylyze what "it" refers to

import sys
sys.path.append('../utility/')

from utility import *
from stanfordcorenlp import StanfordCoreNLP
from const_tree import const_tree
from pattern.en import lemma

import string
from nltk.tag.stanford import StanfordNERTagger
from nltk.tag.stanford import CoreNLPNERTagger
from nltk.parse.corenlp import CoreNLPParser
from utility import *
# from nltk.parse.corenlp import CoreNLPParser
nltk.download('wordnet')
# parser = CoreNLPParser(url='http://nlp01.lti.cs.cmu.edu:9000/')
# def _sentenceToConstTree(sentence):
#     return const_tree.to_const_tree(str(next(parser.raw_parse(sentence))))


# STANFORD_NLP_PATH = "/Users/anitawang/Desktop/11411/NLP/stanford-corenlp-full-2018-02-27"

AUX_VERBS = {'am', 'are', 'is', 'was', 'were', 'being', 'been', 'can', \
             'could', 'dare', 'do', 'does', 'did', 'have', 'has', 'had', 'having', \
             'may', 'might', 'must', 'need', 'ought', 'shall', 'should', 'will', 'would'}
VERB_TYPE_AUX_VERB_MAPPING = {'VB': 'Do', 'VBZ': 'Does', 'VBP': 'Do', 'VBD': 'Did'}
BE_VERBS = {'am', 'is', 'are', 'were', 'was'}
# st = StanfordNERTagger('/Users/anitawang/Desktop/11411/NLP/stanford-ner-2018-02-27/classifiers/english.all.3class.distsim.crf.ser.gz',
#            '/Users/anitawang/Desktop/11411/NLP/stanford-ner-2018-02-27/stanford-ner.jar')
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
        # use POS tagger for pronouns
        if childTag == "PRP" and str.lower(child.word) != "it":
            if result != None and result != "Who": return None
            result = "Who"
    NP_string = const_tree.to_string(np)
    NER_result = ner.tag(NP_string.split())
    # NER tagger for propers
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
        # supersenses
        result = get_supersense(NP_string)

    return result


def generate_wh_question(vp,np):
    # generate wh for the top level NP 
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



# ask wh question on NP at the VP node.
def generate_wh_vp_question(node, parent_NP):
    question = ""
    VP = None
    NP = None # this part to ask!
    VBX = None # for auxiliary verb
    for child in node.children:
        if (child.type == "VP"):
            VP = child
        if (child.type.startswith("VB")):
            VBX = child
        if (child.type == "NP"):
            NP = child
        # Discard sentence with conjunction structure
        if (child.type == "CC"):
            return None

    parent_NP_string = lowercase_if_needed(parent_NP)

    # discard sentence with no VBX
    if VBX == None:
        return
    # if does not have auxiliary verb and does not have NP
    if NP == None and VP == None: return

    # has auxiliary verb
    if (VP != None):
        # add "Wh" in the front and get rid of the NP
        # need to go to the next level and ask what
        NP_AUX = None
        for child in VP.children:
            if (child.type == "NP"):
                NP_AUX = child
        WH = "What"
        if (NP_AUX != None):
            VP.children.remove(NP_AUX)
            # modified to get the corresponding WH word to ask the question
            WH = getWhWord(NP_AUX)
        if not WH:
            WH = "What"
        question +=  WH + " "
        question += VBX.to_string()
        question += " " + parent_NP_string + " " + VP.to_string() + "?"
    # no auxiliary verb
    else:
        # ask what + binary question removing NP
        node.children.remove(NP)
        if VBX.type not in VERB_TYPE_AUX_VERB_MAPPING:
            return None

        # get vp_without_verb
        children_except_VBX = list(filter(lambda child: (not child.type.startswith("VB")), node.children))
        vp_without_verb = " ".join(list(map(lambda child: child.to_string(), children_except_VBX)))
        if vp_without_verb != "":
            vp_without_verb = ' ' + vp_without_verb

        # modified to get the corresponding WH word to ask the question
        WH = getWhWord(NP)
        if not WH:
            WH = "What"
        question +=  WH + " "
        if VBX.to_string() in BE_VERBS:
            question += VBX.to_string() + ' ' + parent_NP_string + vp_without_verb + '?'
        else:
            question += VERB_TYPE_AUX_VERB_MAPPING[VBX.type].lower()
            question += ' ' + parent_NP_string + ' ' + lemma(VBX.to_string()) + vp_without_verb + '?'
    return question


# If there is because in the sentence, generate question asking Why.
def generate_why_question(node, parent_NP):
    question = ""
    SBAR = None
    for child in node.children:
        if (child.type == "SBAR"):
            SBAR = child
        # Discard sentence with conjunction structure
        if (child.type == "CC"):
            return None
    if (SBAR == None or len(SBAR.children) == 0): return None
    # find if there is 'because'
    for child in SBAR.children:
        if (child.word == "because"):
            node.children.remove(SBAR)
            bi_question = analyze_vp_structure(node, parent_NP)
            # lower case the first letter
            if len(bi_question) > 0:
                bi_question = bi_question[0].lower() + bi_question[1:]
            question += "Why "
            question += bi_question
            break
    return question


def generate_questions(root, questionType):

    question = ''
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
    if questionType == 0:
        # binary
        return analyze_vp_structure(vp, np)
    elif questionType == 1:
        # question on NP
        return generate_wh_question(vp, np)
        # question on VP's NP
    elif questionType == 2:
        return generate_wh_vp_question(vp, np)
    else:
        # 3: why questions
        return generate_why_question(vp, np)

def run_generator():
    try:
        input_file = sys.argv[1]
        n_questions = int(sys.argv[2])
    except:
        print "./ask article.txt [nquestions]"
        sys.exit(1)

    with open(input_file, 'r') as f:
        text = f.read()

    sentences = text2sentences(text)

    # remove sentences not ending with '.'

    sentences = [x for x in sentences if x[-1:] is '.']

    nlp_parser = CoreNLPParser(url='http://nlp01.lti.cs.cmu.edu:9000/')
    questions = list()

    total_types = 4
    total_questions = 0

    for sentence in sentences:
        parsed_string = str(next(nlp_parser.raw_parse(sentence)))
        for typeNum in xrange(total_types):
            root = const_tree.to_const_tree(parsed_string)
            q = generate_questions(root, typeNum)
            # here might be a bug, q could be empty instead of None
            if q != None and q!="":
                questions.append(q)
                total_questions += 1
                print q
            if (total_questions >= n_questions):
                return


if __name__ == '__main__':
    run_generator()

                  

