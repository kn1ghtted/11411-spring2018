import sys
sys.path.append('./utility/')
import string
from utility import *
from const_tree import *
from statics import *
from pattern.en import lemma
import string
from nltk.corpus import wordnet as wn
import copy
import pickle
from random import *
import nltk
from tfidf import TfIdfModel
from collections import defaultdict

"""
Functions and constants for ask, generating binary questions
"""

# define answer strings
YES_ANSWER = "Yes."
NO_ANSWER = "No."

WORD_NUMBER_MAPPING = {'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5', 'six': '6', \
                        'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10', 'eleven': '11', \
                        'twelve': '12', 'thirteen': '13', 'fourteen': '14', 'fifteen': '15', \
                        'sixteen': '16', 'seventeen': '17', 'eighteen': '18', 'nineteen': '19', \
                        'twenty': '20'}

def answer_binary_by_comparison(question, sentence):
    """
    Basic idea: for important words in the question, check if it or its synonyms
    exist in the original sentence.
    List of important words' tags:
        numbers: CD
        nouns: NN, NNS, NNP, NNPS
        verbs: VB, VBD, VBG, VBN, VBP, VBZ
        misc: FW
        adjectives: JJ, JJR, JJS
        adverbs: RB, RBR, RBS
    Policies:
        number: check if it or its synonym exists in the original sentence
        noun:
            NN and NNS: check if it or its synonym exists in the original sentence
            NNP and NNPS: check if it exists in the original sentence
        verbs: check if it or its synonym exists in the original sentence
        misc: check if it exists in the original sentence
        adjectives and adverbs:
            check if it exists in the original sentence:
                if yes:
                    continue
                if no:
                    check if its antonyms exist in the original sentence:
    """

    def _check_word_existence(word, word_sets):
        return word.lower() in word_sets or wn.morphy(word) in word_sets or lemma(
            word) in word_sets

    def _check_synonyms_existence(word, word_sets, wn_pos):
        for synsets in wn.synsets(word.lower(), pos=wn_pos):
            for name in synsets.lemma_names():
                if name in word_sets or wn.morphy(name) in word_sets or lemma(
                        name) in word_sets:
                    return True
        return False

    def _check_antonyms_existence(word, word_sets, wn_pos):
        for le in wn.lemmas(word, pos=wn_pos):
            for antonym in le.antonyms():
                name = antonym.name()
                if name in word_sets or wn.morphy(name) in word_sets or lemma(
                        name) in word_sets:
                    return True
        return False

    question = question.translate(None, string.punctuation)
    sentence = sentence.translate(None, string.punctuation)
    word_sets = set()
    for word in sentence.lower().split():
        word_sets.add(word)
        # also adds the word's base form to the sets
        word_sets.add(wn.morphy(word))
        word_sets.add(lemma(word))
    # remove None in the sets
    word_sets = word_sets - {None}
    for word, tag in nltk.pos_tag(nltk.word_tokenize(question))[1:]:
        word = word.lower()
        if tag == 'CD':
            if not _check_word_existence(word, word_sets) and \
                    not _check_synonyms_existence(word, word_sets, None):
                return NO_ANSWER
        elif tag == 'NN' or tag == 'NNS':
            if not _check_word_existence(word, word_sets) and \
                    not _check_synonyms_existence(word, word_sets, wn.NOUN):
                return NO_ANSWER
        elif tag == 'NNP' or tag == 'NNPS':
            if not _check_word_existence(word, word_sets):
                return NO_ANSWER
        elif tag[:2] == 'VB':
            if not _check_word_existence(word, word_sets) and \
                    not _check_synonyms_existence(word, word_sets, wn.VERB):
                return NO_ANSWER
        elif tag[:2] == 'JJ':
            if not _check_word_existence(word, word_sets) and \
                    not _check_synonyms_existence(word, word_sets, wn.ADJ) and \
                    _check_antonyms_existence(word, word_sets, wn.ADJ):
                return NO_ANSWER
        elif tag[:2] == 'RB':
            if not _check_word_existence(word, word_sets) and \
                    not _check_synonyms_existence(word, word_sets, wn.ADV) and \
                    _check_antonyms_existence(word, word_sets, wn.ADV):
                return NO_ANSWER
    return YES_ANSWER

def ask_binary_question(node, parent_NP):
    """
    # Analyze structure of the VP node
    # Split into two cases:
    # 1) VB{P,B,D,Z,N} + ... + VP + ... (am eating a sandwich)
    # 2) VB{P,B,D,Z,N} + ... + NP + ... (ate a sandwich)
    :param node: current VP node
    :param parent_NP: parent NP node
    :return: generated binary question
    """
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


def ask_binary_question2(roots, ners, num):
    """
    @param      roots      List of roots of parsed sentences.
    @param      num        Number of output questions
    
    @return     List of (yes question, no question)
    """
    def _ask_case_1(top_level_np, top_level_vp):
        """
        case 1: VP --> Aux VP
        """
        np_string = lowercase_if_needed(top_level_np)
        vp_copy = copy.deepcopy(top_level_vp)
        aux_node = vp_copy.children[0]
        aux_string = string.capitalize(aux_node.to_string())
        aux_node.word = ''
        vp_string = vp_copy.to_string()
        return aux_string + ' ' + np_string + ' ' + vp_string

    def _ask_case_2(top_level_np, top_level_vp):
        """
        case 2: VP --> Be NP? PP?
        """
        return _ask_case_1(top_level_np, top_level_vp)

    def _ask_case_3(top_level_np, top_level_vp):
        """
        case 3: VP --> Verb NP? PP?
        """
        np_string = lowercase_if_needed(top_level_np)
        vp_copy = copy.deepcopy(top_level_vp)
        verb_node = vp_copy.children[0]
        aux_string = VERB_TYPE_AUX_VERB_MAPPING[verb_node.type]
        verb_node.word = lemma(verb_node.word)
        vp_string = vp_copy.to_string()
        return aux_string + ' ' + np_string + ' ' + vp_string

    def _basic_yes_question(root):
        try:
            if "``" in root.to_string():
                return None

            question = ''

            top_level_np = None
            top_level_vp = None
            top_level_pp = None
            for child in root.children[0].children:
                if child.type == 'NP':
                    top_level_np = child
                if child.type == 'VP':
                    top_level_vp = child
                if child.type == 'PP':
                    top_level_pp = child

            # deal with the case VP --> VP {, and} VP
            if top_level_vp.children[0].type == 'VP':
                top_level_vp = top_level_vp.children[0]

            second_level_vp = None
            second_level_verb = None
            for child in top_level_vp.children:
                if (child.type == "VP"):
                    second_level_vp = child
                if (child.type.startswith("VB")):
                    second_level_verb = child

            if second_level_vp != None:
                question = _ask_case_1(top_level_np, top_level_vp)
            elif second_level_verb.to_string() in BE_VERBS:
                question = _ask_case_2(top_level_np, top_level_vp)
            else:
                question = _ask_case_3(top_level_np, top_level_vp)

            # Refinements
            question = question.replace(' ,', ',')
            question = question.replace(" 's", "'s")
            question = question.replace('-LRB- ', "(")
            question = question.replace(' -RRB-', ")")
            if top_level_pp != None:
                pp_string = top_level_pp.to_string()
                pp_string = pp_string[0].lower() + pp_string[1:]
                question += ' ' + pp_string + '?'
            else:
                question += '?'

            return question
        except:
            return None

    def _convert_to_no_question_number(question):
        words_poss = nltk.pos_tag(nltk.word_tokenize(question))
        for word, pos in words_poss:
            if pos == 'CD':
                original_cd_str = word
                if word in WORD_NUMBER_MAPPING:
                    word = WORD_NUMBER_MAPPING[word]
                try:
                    modified_cd_str = str(int(word) + 1)
                    return question.replace(original_cd_str, modified_cd_str)
                except:
                    pass
        return None

    def _convert_to_no_question_ner(question, ners):
        NER_result = tagger.tag(question.split())
        i = 0
        len_NER_result = len(NER_result)
        local_ners = []
        while i < len_NER_result:
            word = NER_result[i][0]
            tag = NER_result[i][1]
            if tag != 'O':
                i += 1
                while i < len_NER_result and NER_result[i][1] == tag:
                    word += ' ' + NER_result[i][0]
                    i += 1
                local_ners.append((word, tag))
            else:
                i += 1
        local_ners = sorted(local_ners, key=lambda x:len(x[0].split()), reverse=True)
        for word, tag in local_ners:
            try:
                candidates = ners[tag]
                for candidate in candidates:
                    if candidate != word:
                        return question.replace(word, candidate)
            except:
                continue
        return None

    def _convert_to_no_question_adj_adv(question):
        words_poss = nltk.pos_tag(nltk.word_tokenize(question))
        for word, pos in words_poss:
            if pos.startswith('JJ'):
                try:
                    antonym = str(wn.synsets(word, pos=wn.ADJ)[0].lemmas()[0].antonyms()[0].name())
                    return question.replace(word, antonym)
                except:
                    continue
            if pos.startswith('RB'):
                try:
                    antonym = str(wn.synsets(word, pos=wn.ADV)[0].lemmas()[0].antonyms()[0].name())
                    return question.replace(word, antonym)
                except:
                    continue
        return None

    def _check_type_existence(root, type_name):
        if root == None:
            return False
        if root.type.startswith(type_name):
            return True
        for child in root.children:
            if _check_type_existence(child, type_name):
                return True
        return False

    def _assign_score(root, num_words):
        """
        Rules:
        1) Number of words score:
            >=10 <=20       50
            >20 <=30        40
            >30 <=40        30
            >40 <10         10
        2) top-level np has a proper noun:
            20
        3) top-level np has a pronoun:
            -20
        4) top-level vp or pp has a proper noun:
            10
        """
        score = 0
        top_level_np = None
        top_level_vp = None
        top_level_pp = None
        for child in root.children[0].children:
            if child.type == 'NP':
                top_level_np = child
            if child.type == 'VP':
                top_level_vp = child
            if child.type == 'PP':
                top_level_pp = child
        if num_words >= 10 and num_words <= 20:
            score += 50
        elif num_words > 20 and num_words <= 30:
            score += 40
        elif num_words > 30 and num_words <= 40:
            score += 30
        else:
            score += 10
        if _check_type_existence(top_level_np, 'NNP'):
            score += 20
        if _check_type_existence(top_level_np, 'PRP'):
            score -= 20
        if _check_type_existence(top_level_vp, 'NNP') or _check_type_existence(top_level_pp, 'NNP'):
            score += 10

        return score

    ret = []
    for root in roots:
        yes_question = _basic_yes_question(root)
        if yes_question is None:
            continue

        no_question = _convert_to_no_question_ner(yes_question, ners)
        if no_question == None:
            no_question = _convert_to_no_question_adj_adv(yes_question)
        if no_question == None:
            no_question = _convert_to_no_question_number(yes_question)

        score = _assign_score(root, len(yes_question.split()))
        ret.append((yes_question, no_question, score))

    ret = sorted(ret, key=lambda x:x[2], reverse=True)
    return [(x[0], x[1]) for x in ret][:num]

def get_ners(sentences):
    ners = defaultdict(set)
    for sentence in sentences:
        NER_result = tagger.tag(sentence.split())
        i = 0
        len_NER_result = len(NER_result)
        while i < len_NER_result:
            word = NER_result[i][0]
            tag = NER_result[i][1]
            if tag != 'O':
                i += 1
                while i < len_NER_result and NER_result[i][1] == tag:
                    word += ' ' + NER_result[i][0]
                    i += 1
                ners[tag].add(word)
            else:
                i += 1
    for k in ners:
        ners[k] = list(ners[k])
        ners[k] = sorted(ners[k], key=lambda x:len(x.split()), reverse=True)
    return ners


if __name__ == '__main__':
    try:
        input_file = sys.argv[1]
        num_questions = int(sys.argv[2])
    except:
        print "./binary_question article.txt [nquestions]"
        sys.exit(1)

    with open(input_file, 'r') as f:
        text = f.read()

    sentences = text2sentences(text)

    # remove sentences not ending with '.'
    sentences = [x for x in sentences if x[-1:] is '.']
    roots = []
    for sentence in sentences:
        try:
            parsed_string = str(next(parser.raw_parse(sentence)))
            root = const_tree.to_const_tree(parsed_string)
            roots.append(root)
            # print root.to_string()
        except:
            continue

    # with open('roots', 'w+') as f:
    #     pickle.dump(roots, f)
    with open('roots', 'r') as f:
        roots = pickle.load(f)

    ners = get_ners(sentences)

    ret = ask_binary_question2(roots, ners, num_questions)

    sentences = text2sentences(text)

    # the tfidf model that identifies the most relevant
    # sentence to a question
    tfidf = TfIdfModel()
    tfidf.train(sentences)

    # for question, score, expected_answer, root in ret:
    #     print "Sentence: " + root.to_string()
    #     print "Question: " + question
    #     print "Score: " + str(score)
    #     print "Expected answer: " + expected_answer
    #     most_relevant_sentence = tfidf.getNRelevantSentences(question, 1)[0][0]
    #     real_answer = answer_binary_by_comparison(question, most_relevant_sentence)
    #     print "Most Relevant Sentence: " + most_relevant_sentence
    #     print "Real answer: " + real_answer
    #     if expected_answer != real_answer:
    #         print "WRONG ANSWER"
    #     print ""
    for yes_question, no_question in ret:
        print "Yes Question: " + yes_question
        if no_question:
            print "No Question: " + no_question
        print ""