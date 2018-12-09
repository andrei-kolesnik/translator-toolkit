# Imports
import re
from os import listdir
from os.path import isfile, join 
import sys
from io import StringIO
from flask import request
from werkzeug.utils import secure_filename
import scipy
import numpy as np
import pandas as pd
import matplotlib as pl
import nltk
from nltk import FreqDist
nltk.download('punkt')
from nltk import word_tokenize,sent_tokenize
from nltk.corpus import PlaintextCorpusReader

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect)

# Flask  Setup and Routes
app = Flask(__name__)

################################################################################
# Globs
################################################################################
Globs = {
    'file': '',
    'dir': './data/'
}
global docs, docs_processed, sents

excl = ['a', 'after', 'all', 'also', 'an', 'and', 'another', 'any', 'are', 'as', 'at', 'away', 'be', 'been', 'beforehand', 'being', 'both', 'but', 'by', 'can', 'cannot', 'do', 'does', 'each', 'for', 'from', 'further', 'furthermore', 'has', 'have', 'having', 'here', 'hereby', 'hereinabove', 'hereinbefore', 'heretofore', 'how', 'if', 'in', 'into', 'is', 'it', 'its', 'may', 'more', 'no', 'non', 'nor', 'not', 'of', 'off', 'on', 'only', 'or', 'other', 'out', 'own', 'same', 'since', 'so', 'such', 'than', 'that', 'the', 'their', 'then', 'there', 'therebetween', 'thereby', 'therein', 'thereof', 'thereto', 'they', 'this', 'those', 'thus', 'to', 'too', 'up', 'via', 'was', 'what', 'when', 'where', 'wherein', 'whether', 'which', 'whose', 'with', 'within']

################################################################################
# Utils
################################################################################
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


def check():
    if len(Globs['file']) == 0:
        for filename in listdir(Globs['dir']):
            fullname = join(Globs['dir'], filename)
            if isfile(fullname):
                Globs['file'] = filename ##// redo to use the last used
                openfile(filename)


def openfile(filename):
    global docs, docs_processed
    docs = nltk.corpus.PlaintextCorpusReader(Globs['dir'], Globs['file'])
    docs_processed = nltk.Text(docs.words())

################################################################################
# Routs
################################################################################
@app.route("/")
def index():
    return files()


################################################################################
@app.route("/files")
def files():
    global Globs
    files = []
    for filename in listdir(Globs['dir']):
        fullname = join(Globs['dir'], filename)
        if isfile(fullname):
            f = open(fullname)
            files.append({
                "name": filename,
                "first_line": f.readline()
            })
            f.close()
    return render_template("files.html", files = files, globs = Globs)


################################################################################
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    global Globs
    if request.method == 'POST':
        f = request.files['new_file']
        f.save(Globs['dir'] + secure_filename(f.filename))
        Globs['file'] = f.filename
    return files()


################################################################################
@app.route("/f/<name>")
def show_file(name):
    global docs, docs_processed
    Globs['file'] = name
    openfile(name)
    return sents1()


################################################################################
@app.route("/s1")
@app.route("/s1/<word>")
def sents1(word = ''):
    global docs, sents
    check()
    sents = []
    cnt = 1
    for sent in docs.raw().split("\n"):
        sent = sent.strip()
        if len(sent) > 0 and not sent.isspace():
            if len(word) > 0:
                at = sent.find(word)
                if at > -1:
                    sent = sent[:at] + '<span class="sel">' + word + '</span>' + sent[at+len(word)]
                    sents.append({"index": cnt, "sent": sent})
            else:
                sents.append({"index": cnt, "sent": sent})
            cnt = cnt + 1
    return render_template("sents.html", globs = Globs, sents = sents)


################################################################################
@app.route("/s2")
def sents2():
    global docs, sents
    check()
    sents = []
    cnt = 1
    for sent in docs.sents():
        sents.append({"index": cnt, "sent": ' '.join(sent)})
        cnt = cnt+1
    return render_template("sents.html", globs = Globs, sents = sents)


################################################################################
@app.route('/freq')
def freq(): 
    global docs, docs_processed
    check()
    fdist = FreqDist()
    for word in docs.words():
        word = word.lower()
        sans_letters = re.sub(r'[^a-zA-Z]', '', word)
        if (len(word) > 2) and (word not in excl) and (len(word) == len(sans_letters)):
            fdist[word] += 1
    freq_sorted = sorted(fdist.items(), key=lambda item: (item[1], item[0]), reverse=True)
    return jsonify(freq_sorted[:50])


################################################################################
@app.route('/concordance/<word>')
@app.route('/concordance/<word>/<int:count>')
def concordance(word, count = 25): 
    global docs, docs_processed
    check()
    con_list = docs_processed.concordance_list(word, width=80, lines=count)
    con_data = []
    for c in con_list:
        con_data.append({
            "left_print": c.left_print, 
            "query": c.query,
            "right_print": c.right_print})
    return jsonify(con_data)


################################################################################
@app.route('/collocations')
@app.route('/collocations/<int:count>')
def collocations(count = 25): 
    global docs, docs_processed
    check()
    with capt_stdout() as out:
        docs_processed.collocations(num = count)
        collocations_output = out.string
    col_data = []
    for c in collocations_output.split(';'):
        col_data.append({"term": c.strip()})
    return jsonify(col_data)


################################################################################
@app.route('/contexts/<word>')
def contexts(word): 
    global docs, docs_processed
    check()
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


################################################################################
# Main
################################################################################
if __name__ == '__main__':
    app.run(debug=True)
