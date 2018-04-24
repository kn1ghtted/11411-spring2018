from statics import *
import sys
sys.path.append("./utility/")
from utility import *
from const_tree import *
from wh_question import *
from binary_question import *

def generate_adverbial_question(root, node, parent_NP):
    """
    TODO
    :param root: node of the input sentence
    :return: an adverbial question (when, where, how)
    :return: a list of questions or empty list (when, where, how)
    """
    res_q = []
    when_res = ask_when(root, node, parent_NP)
    where_res = ask_where(root, node, parent_NP)
    how_res = ask_how(root, node, parent_NP)
    if when_res != None:
        res_q.append(when_res)
    if where_res != None:
        res_q.append(where_res)
    if how_res != None:
        res_q.append(how_res)
    return res_q

def ask_when(root, node, parent_NP):
    question = ""
    NP_TMP = None
    for child in root.children[0].children:
        if (child.type == "PP"):
            NP_TMP = child
    if (NP_TMP == None or getWhWord(NP_TMP) != "When"):
        for child in node.children:
            if (child.type == "NP-TMP"):
                NP_TMP = child
            # Discard sentence with conjunction structure
            if (child.type == "CC"):
                return None
    if (NP_TMP == None): return None
    # check if there is DATE/TIME
    if getWhWord(NP_TMP) == "When":
        if NP_TMP in root.children[0].children:
            root.children[0].children.remove(NP_TMP)
        else:
            node.children.remove(NP_TMP)
        bi_question = ask_binary_question(node, parent_NP)
        # lower case the first letter
        if len(bi_question) > 0:
            if len(bi_question) > 1:
                bi_question = bi_question[0].lower() + bi_question[1:]
            else:
                bi_question = bi_question[0].lower()
        question += "When "
        question += bi_question
        return question
    return None


def ask_where(root, node, parent_NP):
    question = ""
    PP = None
    for child in root.children[0].children:
        if (child.type == "PP"):
            PP = child
    if (PP == None or getWhWord(PP) != "Where"):
        for child in node.children:
            if (child.type == "PP"):
                PP = child
            # Discard sentence with conjunction structure
            if (child.type == "CC"):
                return None
    if (PP == None): return None
    # check if there is LOCATION
    if getWhWord(PP) == "Where":
        if PP in root.children[0].children:
            root.children[0].children.remove(PP)
        else:
            node.children.remove(PP)
        bi_question = ask_binary_question(node, parent_NP)
        # lower case the first letter
        if len(bi_question) > 0:
            if len(bi_question) > 1:
                bi_question = bi_question[0].lower() + bi_question[1:]
            else:
                bi_question = bi_question[0].lower()
        question += "Where "
        question += bi_question
        return question
    return None

# check if the adv is meaningful to ask
def how_adv(ADVP):
    non_meaningful = ['already', 'also', 'just', 'only', 'often', 'basically', 'however', 'later', 'meanwhile', 'now', 'then','similarly', 'initially', 'for', 'me']
    for child in ADVP.children:
        if child.word != None:
            if child.word.lower() in non_meaningful:
                return False
    return True


def ask_how(root, node, parent_NP):
    question = ""
    ADVP = None
    for child in root.children[0].children:
        if (child.type == "ADVP"):
            ADVP = child
    if (ADVP == None or not(how_adv(ADVP))):
        for child in node.children:
            if (child.type == "ADVP"):
                ADVP = child
            # Discard sentence with conjunction structure
            if (child.type == "CC"):
                return None
    if (ADVP == None): return None
    # check if there is meaningful ADV
    if how_adv(ADVP):
        if ADVP in root.children[0].children:
            root.children[0].children.remove(ADVP)
        else:
            node.children.remove(ADVP)
        bi_question = ask_binary_question(node, parent_NP)
        # lower case the first letter
        if len(bi_question) > 0:
            if len(bi_question) > 1:
                bi_question = bi_question[0].lower() + bi_question[1:]
            else:
                bi_question = bi_question[0].lower()
        question += "How "
        question += bi_question
        return question
    return None


def answer_when(Q, most_relevant_sentence, root, node, parent_NP):
    answer = most_relevant_sentence
    NP_TMP = None
    for child in root.children[0].children:
        if (child.type == "PP"):
            NP_TMP = child
    if (NP_TMP == None or getWhWord(NP_TMP) != "When"):
        for child in node.children:
            if (child.type == "NP-TMP"):
                NP_TMP = child
            # Discard sentence with conjunction structure
            if (child.type == "CC"):
                return answer
    if (NP_TMP == None): return answer
    # check if there is DATE/TIME
    if getWhWord(NP_TMP) == "When":
        answer = NP_TMP.to_string()
        if (len(answer) > 0):
            if (len(answer) > 1):
                answer = answer[0].upper() + answer[1:]
            else:
                answer = answer[0].upper()
        else:
            return answer
        answer += "."
    return answer


def answer_where(Q, most_relevant_sentence, root, node, parent_NP):
    answer = most_relevant_sentence
    PP = None
    for child in root.children[0].children:
        if (child.type == "PP"):
            PP = child
    if (PP == None or getWhWord(PP) != "Where"):
        for child in node.children:
            if (child.type == "PP"):
                PP = child
            # Discard sentence with conjunction structure
            if (child.type == "CC"):
                return answer
    if (PP == None): return answer
    # check if there is LOCATION
    if getWhWord(PP) == "Where":
        answer = PP.to_string()
        if (len(answer) > 0):
            if (len(answer) > 1):
                answer = answer[0].upper() + answer[1:]
            else:
                answer = answer[0].upper()
        else:
            return answer
        answer += "."
    return answer

def answer_how(Q, most_relevant_sentence, root, node, parent_NP):
    answer = most_relevant_sentence
    ADVP = None
    for child in root.children[0].children:
        if (child.type == "ADVP"):
            ADVP = child
    if (ADVP == None or not(how_adv(ADVP))):
        for child in node.children:
            if (child.type == "ADVP"):
                ADVP = child
            # Discard sentence with conjunction structure
            if (child.type == "CC"):
                return answer
    if (ADVP == None): return answer
    # check if there is meaningful ADV
    if how_adv(ADVP):
        answer = ADVP.to_string()
        if (len(answer) > 0):
            if (len(answer) > 1):
                answer = answer[0].upper() + answer[1:]
            else:
                answer = answer[0].upper()
        else:
            return answer
        answer += "."
    return answer

