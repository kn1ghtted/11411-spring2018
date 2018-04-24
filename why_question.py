

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
                bi_question = bi_question[0].lower() + bi_question[1:]
            question += "Why "
            question += bi_question
            break
    return question


def answer_why(Q):
    return None