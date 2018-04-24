

from statics import *
import sys
sys.path.append("./utility/")
from utility import *
from const_tree import *
from pattern.en import lemma
from binary_question import *

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
            bi_question = ask_binary_question(node, parent_NP)
            # lower case the first letter
            if len(bi_question) > 0:
                if len(bi_question) > 1:
                    bi_question = bi_question[0].lower() + bi_question[1:]
                else:
                    bi_question = bi_question[0].lower()
            question += "Why "
            question += bi_question
            break
    return question


def answer_why(Q, most_relevant_sentence, node, parent_NP):
    answer = most_relevant_sentence
    SBAR = None
    for child in node.children:
        if (child.type == "SBAR"):
            SBAR = child
        # Discard sentence with conjunction structure
        if (child.type == "CC"):
            return answer
    if (SBAR == None or len(SBAR.children) == 0): return answer
    # find if there is 'because'
    del_child = []
    for child in SBAR.children:
        if (child.word == "because"):
            # Answer with because
            for c in del_child:
                SBAR.children.remove(c)
            answer = SBAR.to_string()
            if (len(answer) > 0):
                if (len(answer) > 1):
                    answer = answer[0].upper() + answer[1:]
                else:
                    answer = answer[0].upper()
            else:
                return answer
            answer += "."
            break
        else:
            del_child.append(child)
    return answer

