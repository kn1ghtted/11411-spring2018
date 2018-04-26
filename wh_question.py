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

def check_type_existence(root, checkFunction):
        if root == None:
            return False
        if root.word and checkFunction(root):
            return True
        for child in root.children:
            if check_type_existence(child, checkFunction):
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
    np_string = np.to_string()
    if Qtype == "Who":
        if childIsPerson(child):
            if child.word not in Q:
                if child.word == "I":
                    return "Me."
                return np_string[0].upper() + np_string[1:] + "."
    elif Qtype == "What":
        if childIsObject(child):
            if child.word not in Q:
                return np_string[0].upper() + np_string[1:] + "."



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
            return result[0].upper() + result[1:]


        # if asking about NP in VP
        VP_NP = None
        for child in vp.children:
            if child.type == "NP":
                VP_NP = child
        if VP_NP:
            for child in VP_NP.children:
                if child.word:
                    result = checkChildIsAnswer(Q, Qtype, child, VP_NP)

                else:
                    for grandchild in child.children:
                        if grandchild.word:
                            result = checkChildIsAnswer(Q, Qtype, grandchild, VP_NP)
                if result:
                    return result

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
                result = "What"
                # result = "Which" + " " + label[5:]
            elif label == "noun.quantity":
                result = "How many"
    return result


def get_supersense_pp_advp_sbar(node):
    labelSet = set([])
    for child in node.children:
        try:
            labelSet = labelSet.union(get_word_supersenses(child))
        except:
            continue

    if "noun.location" in labelSet:
        return "Where"
    if "noun.time" in labelSet:
        return "When"
    return None


def get_labelset_from_node(n):
    """
    Grab label set for everything
    :param n:
    :return:
    """
    ret = set([])
    for word in n.to_string().split():
        try:
            S = get_word_supersenses(word)
        except:
            continue
        ret = ret.union(S)
    return ret

def get_supersense_np(np):

    """
    Deal with the following cases:
        a) parallel NPs -> use last word
        b) NP's NP -> use the latter (This is same as first case)
        c) NP PP (e.g.: Lebron James of Cleveland Cavaliers) -> use the first NP
        d) NP SBAR (e.g. the food that I like) -> use the first NP

    """

    labelSet = None
    # search for SBAR or PP
    for i in xrange(len(np.children)):
        child = np.children[i]
        if child.type in ["PP", "SBAR"]:
            if i > 0:
                target = np.children[i - 1]
                # if target is capitalized, we already know it's not NER
                if (target.to_string()[0].isupper()):
                    return "What"
                labelSet = get_labelset_from_node(target)
                break
            else:
                return None

    # no PP or SBAR found, use the last word

    # if target is capitalized, we already know it's not NER
    if (np.children[-1].to_string()[0].isupper()):
        return "What"

    if labelSet is None:
        labelSet = get_labelset_from_node(np.children[-1])


    for label in labelSet:
        if label.startswith("noun."):
            if label == "noun.person":
                return "Who"
            if label in whatSet:
                return "What"
            elif label in whichSet:
                return "What"
                # return "Which" + " " + label[5:]
            elif label == "noun.quantity":
                return "How many"
    return None


def getWhWordNP(node):

    for child in node.children:
        childTag = child.type
        # use POS tagger for pronouns
        if childTag.startswith("PRP") and str.lower(child.word) != "it":
            return None
        elif child.word and str.lower(child.word) == "it":
            return None

    NP_string = const_tree.to_string(node)
    NER_result = tagger.tag(NP_string.split())
    # NER tagger for propers

    for (word, tag) in NER_result:
        if tag in ["PERSON", "ORGANIZATION"]:
            return "Who"
        elif tag == "MONEY":
            return "How much"

    return get_supersense_np(node)

def getWhWord_PP_ADVP_SBAR(node):
    NP_string = node.to_string()
    if node.type == "SBAR":
        if "when" in NP_string.lowercase() or "while" in NP_string.lowercase():
            return "When"
        if "where" in NP_string.lowercase():
            return "Where"

    NER_result = tagger.tag(NP_string.split())

    for (word, tag) in NER_result:
        if tag in ["TIME", "DATE"]:
            return "When"
        elif tag in ["LOCATION"]:
            return "Where"

    return get_supersense_pp_advp_sbar(node)


def getWhWord(node):
    """
    Take in node representing an interested phrase in the original sentence,
    e.g.: "The film", "into the jungle", "in 2016"

    :param node:
    :return: Case on the node's type in the original sentence, output what type of Q
    can be asked
    """

    result = None

    if node.type.startswith("NP"):
        return getWhWordNP(node)

    if node.type in ["PP", "ADVP", "SBAR"]:
        return getWhWord_PP_ADVP_SBAR(node)

    else:
        # Unknown/unimplemented type of node
        return None


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