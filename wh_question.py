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
        elif tag == "GPE":
            if result != None and result != "GPE": return None
            result = "Where"
    if not result:
        # supersenses
        result = get_supersense(NP_string)

    return result


def generate_wh_np_question(vp, np):
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