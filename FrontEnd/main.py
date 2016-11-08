from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from ES_query import get_results_ES, get_results_LDA
from gensim import corpora, models, similarities

app = Flask(__name__)
app.config.from_envvar('FLASK_SETTINGS', silent=True)

models_directory = 'TopicModels/'
w_dict = corpora.Dictionary.load(models_directory + 'wikia_docs.dict')
w_lda = models.ldamodel.LdaModel.load(models_directory + 'wikia_docs.model')
w_index = similarities.MatrixSimilarity.load(models_directory + "wikia_docs.index")
c_dict = corpora.Dictionary.load(models_directory + 'char_docs.dict')
c_lda = models.ldamodel.LdaModel.load(models_directory + 'char_docs.model')
c_index = similarities.MatrixSimilarity.load(models_directory + "char_docs.index")
w_docs = []
c_docs = []
with open('parsed_docs_path.txt', 'r') as f:
    for line in f:
        w_docs.append(line.strip())
with open('parsed_char_path.txt', 'r') as f:
    for line in f:
        c_docs.append(line.strip())
a='ES'


@app.route('/')
def hello():
    return render_template('search.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    global a
    if request.method == 'POST':

        search_request = request.form['request']
        if search_request == 'ES':
            a = 'ES'
        if search_request == 'LDA':
            a = 'LDA'
        try:
            if a == 'ES':
                entries = get_results_ES(search_request)
            else:
                entries = get_results_LDA(search_request, w_dict, w_lda, w_index, w_docs, c_dict, c_lda, c_index,
                                          c_docs)
                print('yse')
        except Exception as e:
            print(e)
        return render_template('search_results.html', search_request=search_request, entries=entries)


if __name__ == '__main__':
    app.run()
