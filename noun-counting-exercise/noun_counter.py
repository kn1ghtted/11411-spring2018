from stanfordcorenlp import StanfordCoreNLP
import json
import gzip
import os

# a class for rapping nlp interface
# reference: https://www.khalidalnajjar.com/setup-use-stanford-corenlp-server-python/


class StanfordNLP:
    def __init__(self, host='http://localhost', port=9000):
        self.nlp = StanfordCoreNLP(host, port=port,
                                   timeout=30000)  # , quiet=False, logging_level=logging.DEBUG)
        self.props = {
            'annotators': 'tokenize,ssplit,pos,lemma,ner,parse,depparse,dcoref,relation',
            'pipelineLanguage': 'en',
            'outputFormat': 'json'
        }

    def word_tokenize(self, sentence):
        return self.nlp.word_tokenize(sentence)

    def pos(self, sentence):
        return self.nlp.pos_tag(sentence)

    def ner(self, sentence):
        return self.nlp.ner(sentence)

    def parse(self, sentence):
        return self.nlp.parse(sentence)

    def dependency_parse(self, sentence):
        return self.nlp.dependency_parse(sentence)

    def annotate(self, sentence):
        return json.loads(self.nlp.annotate(sentence, properties=self.props))

    @staticmethod
    def tokens_to_dict(_tokens):
        tokens = dict() 
        for token in _tokens:
            tokens[int(token['index'])] = {
                'word': token['word'],
                'lemma': token['lemma'],
                'pos': token['pos'],
                'ner': token['ner']
        }
        return tokens




# class for the handling noun counting exercise


class NounCounter:

    DATASET_3_PATH = "../data/set3/"
    OUTPUT_PATH = "noun_count.txt"

    # read from input texts and store as a list of strings
    def get_files(self):

        contents = []

        for filename in self.files:
            with open(NounCounter.DATASET_3_PATH + filename, "r") as F:
                lines = F.readlines()
                lines = [line.strip() for line in lines]
                text = " ".join(lines)
                words = text.split(" ")
                words = [word for word in words if word != ""]
                text = " ".join(words)
                contents.append(text)

        return contents

    def __init__(self):
        self.files = [f for f in os.listdir(NounCounter.DATASET_3_PATH) if f.endswith("txt")]
        self.contents = self.get_files()

    def tag_contents(self):
        output = []
        for i in xrange(len(self.contents)):
            text = self.contents[i]
            counter = 0
            texts = text.split()
            half_index = len(texts)/2

            tagged_strings = sNLP.pos(" ".join(texts[:half_index]))
            # print text

            # go through one file
            for (word, tag) in tagged_strings:
                # convert from unicode to ascii
                tag_string = tag.encode("utf8")
                if tag_string.startswith("N"):
                    counter += 1


            tagged_strings = sNLP.pos(" ".join(texts[half_index:]))
            # print text

            # go through one file
            for (word, tag) in tagged_strings:
                # convert from unicode to ascii
                tag_string = tag.encode("utf8")
                if tag_string.startswith("N"):
                    counter += 1
            output.append((self.files[i], counter))

        # write results to OUTPUT_PATH
        with open(NounCounter.OUTPUT_PATH, "w") as F:
            for (filename, count) in output:
                F.write("{}: {}\n".format(filename, count,))


def demo(sNLP):
    text = 'A blog post using Stanford CoreNLP Server.'
    print "Annotate:", sNLP.annotate(text)
    print "POS:", sNLP.pos(text)
    print "Tokens:", sNLP.word_tokenize(text)
    print "NER:", sNLP.ner(text)
    print "Parse:", sNLP.parse(text)
    print "Dep Parse:", sNLP.dependency_parse(text)

if __name__ == '__main__':
    sNLP = StanfordNLP()
    NC = NounCounter()
    NC.tag_contents()
    # demo(sNLP)
