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
# from nltk.parse.corenlp import CoreNLPParser
nltk.download('wordnet')

# parser = CoreNLPParser(url='http://nlp01.lti.cs.cmu.edu:9000/')
# def _sentenceToConstTree(sentence):
#     return const_tree.to_const_tree(str(next(parser.raw_parse(sentence))))

st = StanfordNERTagger('/Users/Jing/Desktop/s18/11411/project/stanford-ner-2018-02-27/classifiers/english.all.3class.distsim.crf.ser.gz',
           '/Users/Jing/Desktop/s18/11411/project/stanford-ner-2018-02-27/stanford-ner.jar')

STANFORD_NLP_PATH = "/Users/Jing/Desktop/s18/11411/project/stanford-corenlp-full-2018-02-27"
# STANFORD_NLP_PATH = "/Users/teddyding/11411/stanford-corenlp-full-2017-06-09"
#STANFORD_NLP_PATH = "/home/lxy/stanford-corenlp-full-2017-06-09"

AUX_VERBS = {'am', 'are', 'is', 'was', 'were', 'being', 'been', 'can', \
             'could', 'dare', 'do', 'does', 'did', 'have', 'has', 'had', 'having', \
             'may', 'might', 'must', 'need', 'ought', 'shall', 'should', 'will', 'would'}
VERB_TYPE_AUX_VERB_MAPPING = {'VB': 'Do', 'VBZ': 'Does', 'VBP': 'Do', 'VBD': 'Did'}
BE_VERBS = {'am', 'is', 'are', 'were', 'was'}




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


def generate_whh_question(sentence):
    print "[Sentence] ", sentence
    question = ''
    parsed_string = nlp.parse(sentence)
    # print (nlp.parse('I ate a sandwich.'))
    # print (nlp.parse('I have eaten a sandwich.'))
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
    # return analyze_vp_structure(vp, np)
    # return generate_wh_vp_question(vp, np)
    return generate_why_question(vp, np)

def generate_binary_question(sentence):
    print "[Sentence] ", sentence
    question = ''
    parsed_string = nlp.parse(sentence)
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
    return analyze_vp_structure(vp, np)

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
        VP.children.remove(child)
        question += "What" + " " # need to modify to ask different Wh questions !!!!!!!!!!!!!!!!!!!!
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

        # ask question starting with Wh !!!!!!!!!!!!!!!!!!!!!
        question += "What" + " "
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


if __name__ == '__main__':
    input_file = 'sample_input.txt'
    with open(input_file, 'r') as f:
        text = f.read()

    sentences = text2sentences(text)

    # remove sentences not ending with '.'
    sentences = [x for x in sentences if x[-1:] is '.']

    nlp = StanfordCoreNLP(STANFORD_NLP_PATH)

    questions = list()
    # print(generate_binary_question('I ate a sandwich.'))
    # print(generate_binary_question('I have eaten a sandwich.'))
    print (nlp.parse('I talk to a person because I like talking.'))
    sentence_test = 'I talk to a person because I like talking.'
    print ("get question")
    print generate_whh_question(sentence_test)

    sentence_test2 = "Hazanavicius chose the form of the melodrama, mostly because he thought many of the films from the silent era which have aged best are melodramas."
    print (nlp.parse(sentence_test2))
    print "another question"
    print generate_whh_question(sentence_test2)

    # STANFORD_NLP_PATH = "/Users/teddyding/11411/stanford-corenlp-full-2017-06-09"

    # nlp = StanfordCoreNLP(STANFORD_NLP_PATH)
    # sentence = 'The teacher appeared at the police station yesterday.'
    # tokens = nlp.word_tokenize(sentence)
    # pos = nlp.pos_tag(sentence)
    # tree = nlp.parse(sentence)
    # print nlp.ner(sentence)
    # ner = CoreNLPNERTagger(url='http://nlp01.lti.cs.cmu.edu:9000/')
    # print ner.tag("I talk to a person.".split())
    # print get_word_supersense("person")

    for sentence in sentences:
        question1 = generate_binary_question(sentence)
        question2 = generate_whh_question(sentence)
        # if (question1 is not None) and (question2 is not None):
        #     questions.append(question1)
        #     questions.append(question2)
        #     print "[Question] ", question1
        #     print "[Question] ", question2
        #     print '\n'

    nlp.close()