# Imports
import re
import scipy
import numpy as np
import pandas as pd
import matplotlib as pl
import nltk
from nltk import FreqDist

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)

# Flask  Setup and Routes
app = Flask(__name__)

# Prepare the document
from nltk.corpus import PlaintextCorpusReader
corpus_loc = './data/'
docs = nltk.corpus.PlaintextCorpusReader(corpus_loc, '.*\.txt')
docs_processed = nltk.Text(docs.words())
sents = []
cnt = 1
for sent in docs.sents():
    sents.append({"index": cnt, "sent": ' '.join(sent)})
    cnt = cnt+1

excl = ['a', 'after', 'all', 'also', 'an', 'and', 'another', 'any', 'are', 'as', 'at', 'away', 'be', 'been', 'beforehand', 'being', 'both', 'but', 'by', 'can', 'cannot', 'do', 'does', 'each', 'for', 'from', 'further', 'furthermore', 'has', 'have', 'having', 'here', 'hereby', 'hereinabove', 'hereinbefore', 'heretofore', 'how', 'if', 'in', 'into', 'is', 'it', 'its', 'may', 'more', 'no', 'non', 'nor', 'not', 'of', 'off', 'on', 'only', 'or', 'other', 'out', 'own', 'same', 'since', 'so', 'such', 'than', 'that', 'the', 'their', 'then', 'there', 'therebetween', 'thereby', 'therein', 'thereof', 'thereto', 'they', 'this', 'those', 'thus', 'to', 'too', 'up', 'via', 'was', 'what', 'when', 'where', 'wherein', 'whether', 'which', 'whose', 'with', 'within']

import sys
from io import StringIO

# Class to capture output of functions with no return
class capt_stdout:
    def __init__(self):
        self._stdout = None
        self._string_io = None

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._string_io = StringIO()
        return self

    def __exit__(self, type, value, traceback):
        sys.stdout = self._stdout

    @property
    def string(self):
        return self._string_io.getvalue()

# Create route that renders index.html template
@app.route("/")
def index():
    return render_template("index.html", sents = sents)

@app.route('/freq')
def freq(): 
    fdist = FreqDist()
    for word in docs.words():
        word = word.lower()
        sans_letters = re.sub(r'[^a-zA-Z]', '', word)
        if (len(word) > 2) and (word not in excl) and (len(word) == len(sans_letters)):
            fdist[word] += 1
    freq_sorted = sorted(fdist.items(), key=lambda item: (item[1], item[0]), reverse=True)
    return jsonify(freq_sorted[:50])

@app.route('/concordance/<word>/<int:count>')
def concordance(word, count = 25): 
    con_list = docs_processed.concordance_list(word, width = 80, lines = count)   
    con_data = []
    for c in con_list:
        con_data.append({
            "left_print": c.left_print, 
            "query": c.query,
            "right_print": c.right_print})
    return jsonify(con_data)

@app.route('/contexts/<word>')
def contexts(word): 
    with capt_stdout() as out:
        docs_processed.common_contexts([word])
        common_contexts_output = out.string
    con_data = []
    for c in common_contexts_output.split():
        ind = c.find('_')
        if ind > -1:            
            con_data.append({
                "left_print": c[:ind], 
                "query": word,
                "right_print": c[ind+1:]})

    return jsonify(con_data)

if __name__ == '__main__':
    app.run(debug=True)
