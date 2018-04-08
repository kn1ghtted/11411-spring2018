#!/usr/bin/env python

from qg import text2sentences
from tfidf import TfIdfModel

if __name__ == '__main__':
    input_file = 'sample_input.txt'
    with open(input_file, 'r') as f:
        text = f.read()

    sentences = text2sentences(text)

    model = TfIdfModel()
    model.train(sentences)

    question0 = "Did the Artist receive highly positive reviews from critics and won many accolades?"
    results0 = model.getNRelevantSentences(question0,2)
    print "Sample Question: " + question0
    print "Top 2 relevant sentences: " + str(results0)

    question1 = "What became the most awarded French film in history?"
    results1 = model.getNRelevantSentences(question1,2)
    print "Sample Question: " + question1
    print "Top 2 relevant sentences: " + str(results1)
