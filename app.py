# Imports
import re
from os import listdir
from os.path import isfile, join 
import sys
from io import StringIO
from collections import defaultdict
from flask import request
from werkzeug.utils import secure_filename
import scipy
# import numpy as np
# import pandas as pd
# import matplotlib as pl
import nltk
from nltk import FreqDist
nltk.download('punkt')
nltk.download('words')
from nltk.corpus import words
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
global text, text_proc, sents, text_detailed, text_vocab, english_vocab

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
    global Globs, text, text_proc, text_detailed, text_vocab, english_vocab
    Globs['file'] = filename
    text = nltk.corpus.PlaintextCorpusReader(Globs['dir'], Globs['file'])
    text_proc = nltk.Text(text.words())
# extra part
    stemmer = nltk.PorterStemmer() # nltk.LancasterStemmer()
    text_detailed = []
    cnt = 1
    for sent in text.raw().split("\n"):
        sent = sent.strip()
        if len(sent) > 0 and not sent.isspace():
            tokenized = nltk.word_tokenize(sent)
            words = []
            stems = []
            for tok in tokenized:
                words.append(tok)  # .lower()
                stems.append(stemmer.stem(tok))
            text_detailed.append({"index": cnt, "sent": sent, "words": words, "stems": stems})
            cnt = cnt + 1
    text_vocab = set(w.lower() for w in text.words() if w.isalpha())
    english_vocab = set(w.lower() for w in nltk.corpus.words.words()) # we can move it so it can only executed once


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
    openfile(name)
    return sents1()


################################################################################
@app.route("/s1")
@app.route("/s1/<word>")
def sents1(word=''):
    global text, sents
    check()
    sents = []
    cnt = 1
    for sent in text.raw().split("\n"):
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
    global text, sents
    check()
    sents = []
    cnt = 1
    for sent in text.sents():
        sents.append({"index": cnt, "sent": ' '.join(sent)})
        cnt = cnt+1
    return render_template("sents.html", globs = Globs, sents = sents)


################################################################################
@app.route("/s3")
@app.route("/s3/<stem>")
def sents3(stem=''):
    global text_detailed
    sents = []
    for sent in text_detailed:
        # at = sent.find(word)
        # if at > -1:
        #     sent = sent[:at] + '<span class="sel">' + word + '</span>' + sent[at+len(word)]
        if stem in sent['stems']:
            for i, s in enumerate(sent['stems']):
                if s == stem:
                    sent['words'][i] = '<span class="sel">' + sent['words'][i] + '</span>'
            sents.append({
                    'index': sent['index'],
                    'sent': ' '.join(sent['words']) # sent['sent']
                })
    return jsonify(sents)


################################################################################
@app.route('/freq')
# def freq():
#     global text, text_proc
#     check()
#     fdist = FreqDist()
#     for word in text.words():
#         word = word.lower()
#         sans_letters = re.sub(r'[^a-zA-Z]', '', word)
#         if (len(word) > 2) and (word not in excl) and (len(word) == len(sans_letters)):
#             fdist[word] += 1
#     freq_sorted = sorted(fdist.items(), key=lambda item: (item[1], item[0]), reverse=True)
#     return jsonify(freq_sorted[:50])
def freq():
    global text, text_proc
    check()
    tokens = nltk.word_tokenize(text.raw())
    stemmer = nltk.PorterStemmer() # nltk.LancasterStemmer()
    dd = defaultdict(list)
    fdist = FreqDist()
    prog = re.compile(r'^[a-zA-Z][a-zA-Z\\\-]+[a-zA-Z]$')
    for tok in tokens:
        tok = tok.lower()
        if prog.match(tok) and tok not in excl:
            stem = stemmer.stem(tok)
            if tok not in dd[stem]:
                dd[stem].append(tok)
            fdist[stem] += 1
    result = []
    for stem in sorted(dd.keys()):
            result.append({
                "words": ' '.join(dd[stem]),
                "count": fdist[stem],
                "stem": stem
            })
    return jsonify(result)

################################################################################
@app.route('/unusual')
def unusual():
    global text, text_proc, text_vocab, english_vocab
    check()
    unusual = text_vocab.difference(english_vocab)
    tokens = nltk.word_tokenize(text.raw())
    stemmer = nltk.PorterStemmer()  # nltk.LancasterStemmer()
    dd = defaultdict(list)
    fdist = FreqDist()
    prog = re.compile(r'^[a-zA-Z][a-zA-Z\\\-]+[a-zA-Z]$')
    for tok in tokens:
        tok = tok.lower()
        if prog.match(tok) and tok not in excl and tok in unusual:
            stem = stemmer.stem(tok)
            if tok not in dd[stem]:
                dd[stem].append(tok)
            fdist[stem] += 1
    result = []
    for stem in sorted(dd.keys()):
            result.append({
                "words": ' '.join(dd[stem]),
                "count": fdist[stem],
                "stem": stem
            })
    return jsonify(result)


################################################################################
@app.route('/concordance/<word>')
@app.route('/concordance/<word>/<int:count>')
def concordance(word, count = 25): 
    global text, text_proc
    check()
    con_list = text_proc.concordance_list(word, width=80, lines=count)
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
    global text, text_proc
    check()
    with capt_stdout() as out:
        text_proc.collocations(num = count)
        collocations_output = out.string
    col_data = []
    for c in collocations_output.split(';'):
        col_data.append({"term": c.strip()})
    return jsonify(col_data)


################################################################################
@app.route('/contexts/<word>')
def contexts(word): 
    global text, text_proc
    check()
    with capt_stdout() as out:
        text_proc.common_contexts([word])
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
@app.route('/step1')
def step1():
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
    return render_template("steps.html", files=files, globs=Globs)

@app.route('/step2/<filename>')
def step2(filename):
    global text
    openfile(filename)
    result = text.raw().replace('\r\n', '<br>')
    return jsonify(result)


@app.route('/step3')
def step3():
    global text
    tokens = nltk.word_tokenize(text.raw())
    stemmer = nltk.PorterStemmer() # nltk.LancasterStemmer()
    dd = defaultdict(list)
    fdist = FreqDist()
    result = []
    prog = re.compile(r'^[a-zA-Z][a-zA-Z\\\-]+[a-zA-Z]$')
    for tok in tokens:
        tok = tok.lower()
        # sans_letters = re.sub(r'[^a-zA-Z\-\\]', '', tok)
        stem = stemmer.stem(tok)
        # if len(tok) == len(sans_letters) and tok not in excl:
        if prog.match(tok) and tok not in excl:
            if tok not in dd[stem]:
                dd[stem].append(tok)
            fdist[stem] += 1
    for stem in sorted(dd.keys()):
            result.append({
                "stem": stem,
                "count": fdist[stem],
                "words": ' '.join(dd[stem])
            })
    return jsonify(result)


################################################################################
# Main
################################################################################
if __name__ == '__main__':
    app.run(debug=True)
