"""
Question type 1 and 2:
what, who questions on subjects and objects
"""

from statics import *
import sys
sys.path.append("./utility/")
from utility import *
from const_tree import *
from pattern.en import lemma
from tfidf import TfIdfModel
whichSet = set(['noun.feeling',  'noun.group', 'noun.location',  'noun.shape', 'noun.state'])
whatSet = set(['noun.artifact', 'noun.attribute', 'noun.body', 'noun.cognition', 'noun.communication',\
    'noun.event', 'noun.food',  'noun.motive',\
     'noun.object', 'noun.phenomenon', 'noun.plant', 'noun.possession',\
    'noun.process', 'noun.quantity', 'noun.relation'])

def check_type_existence(root, type_name):
        if root == None:
            return False
        if root.type.startswith(type_name):
            return True
        for child in root.children:
            if _check_type_existence(child, type_name):
                return True
        return False

def childIsObject(child):
    # child is a node
    try:
        labels = get_word_supersenses(child.word)
    except:
        return False
    for eachLabel in labels:
        if eachLabel in whatSet:
            return True
    return False


def childIsPerson(child):
    if child.type == "PRP" or child.type == "NNP":
        return True
    try:
        labels = get_word_supersenses(child.word)
    except:
        return False
    if "noun.person" in labels:
        return True
    return False

def checkChildIsAnswer(Q,Qtype,child,np):
    if Qtype == "Who":
        if childIsPerson(child):
            if child.word not in Q:
                if child.word == "I":
                    return "Me."
                return np.to_string() + "."
    elif Qtype == "What":
        if childIsObject(child):
            if child.word not in Q:
                return np.to_string() + "."



def NP_answer_helper(Q, relSentence, Qtype):
    parsed_sentence = str(next(parser.raw_parse(relSentence)))
    sentence_node = const_tree.to_const_tree(parsed_sentence)
    result = None
    for child in sentence_node.children[0].children:
        if child.type == 'NP':
            np = child
        if child.type == 'VP':
            vp = child
    
    if np == None:
        # return default answer
        return relSentence
    else:
        # if asking about top level NP
        for child in np.children:
            if child.word:
                result = checkChildIsAnswer(Q, Qtype, child, np)
            else:
                for grandchild in child.children:
                    if grandchild.word:
                        result = checkChildIsAnswer(Q, Qtype, grandchild, np)
        if result:
            return result


        # if asking about NP in VP
        VP_NP = None
        for child in vp.children:
            if child.type == "NP":
                VP_NP = child
        if VP_NP:
            for child in VP_NP.children:
                if child.word:
                    return checkChildIsAnswer(Q, Qtype, child, VP_NP)
                else:
                    for grandchild in child.children:
                        if grandchild.word:
                            return checkChildIsAnswer(Q, Qtype, grandchild, VP_NP)

    return relSentence




def answer_who(Q, relSentence):
    return NP_answer_helper(Q, relSentence, "Who")


def answer_what(Q, relSentence):
    return NP_answer_helper(Q, relSentence, "What")


def getWhFromLabel(label):
    result = None
    if label == "noun.person":
        result = "Who"
    else:
        if label.startswith("noun."):
            if label in whatSet:
                result = "What"
            elif label in whichSet:
                result = "Which" + " " + label[5:]
            elif label == "noun.quantity":
                result = "How many"
    return result

def get_supersense(np):
    result = None
    nounCount = 0
    totalLabel = []
    np_string = const_tree.to_string(np)
    for word in np_string.split(" "):
        try:
            labelSet = get_word_supersenses(word)
        except:
            labelSet = set()
            continue
        # if is person
        totalLabel = totalLabel + [labelSet]
        for eachLabel in labelSet:
            # count the number of possible nouns in NP
            if eachLabel.startswith("noun."):
                nounCount += 1
                break
    if nounCount > 1:
        # TODO: Multiple noun situation
        # if all Nouns are parallel, find the last one
        isParallel = True
        for child in np.children:
            if child.word == None:
                isParallel = False
        if isParallel:
            for i in xrange(len(totalLabel)-1,-1,-1):
                labetSet =totalLabel[i]
                for label in labelSet: 
                    label
                    result = getWhFromLabel(label)
                    if result:
                        return result
                
        else:
            # TODO: deal with non parallel nouns
            return None
    else:

        for labelset in totalLabel:
            for label in labelset:
                result = getWhFromLabel(label)
                if result:
                    return result
    return result


# takes in a NP node
def getWhWord(node):
    result = None
    for child in node.children:
        childTag = child.type
        # use POS tagger for pronouns
        if childTag == "PRP" and str.lower(child.word) != "it":
            if result != None and result != "Who": return None
            result = "Who"
        elif child.word and str.lower(child.word) == "it":
            return None
    NP_string = const_tree.to_string(node)
    NER_result = tagger.tag(NP_string.split())
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

    if not result:
        result = get_supersense(node)

    return result


def generate_wh_np_question(vp, np):
    # generate wh for the top level NP
    question = ""
    hasPerson = False
    WH = getWhWord(np)

    if not WH:
        return None
    question +=  WH + " "
    VBX = None
    verb = None
    for child in vp.children:
        if child.type.startswith("VB"):
            VBX = child

    if (VBX != None) and (VBX.word != None) and (VBX.word in BE_VERBS):
        if VBX.word == "am" or VBX.word == "is":
            verb = "is"
        else:
            verb = VBX.word
  
    
    #get vp without verb
    children_except_VBX = list(filter(lambda child: (not child.type.startswith("VB")), vp.children))
    vp_without_verb = " ".join(list(map(lambda child: child.to_string(), children_except_VBX)))
    if vp_without_verb != "":
        vp_without_verb = ' ' + vp_without_verb

    if verb:
        rest = verb + vp_without_verb
    else:
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
        return None
    if VBX.word and str.lower(VBX.word) in BE_VERBS:
        return None
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
        else:
            return None
        if WH:
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
        if WH:
            question +=  WH + " "
            if VBX.to_string() in BE_VERBS:
                question += VBX.to_string() + ' ' + parent_NP_string + vp_without_verb + '?'
            else:
                question += VERB_TYPE_AUX_VERB_MAPPING[VBX.type].lower()
                question += ' ' + parent_NP_string + ' ' + lemma(VBX.to_string()) + vp_without_verb + '?'
    return question