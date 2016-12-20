from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from ES_query import get_results_ES, get_results_LDA, get_results
from gensim import corpora, models, similarities
import json

app = Flask(__name__)
app.config.from_envvar('FLASK_SETTINGS', silent=True)

models_directory = 'TopicModels/'
w_dict = corpora.Dictionary.load(models_directory + 'wikia_docs.dict')
w_lda = models.ldamodel.LdaModel.load(models_directory + 'wikia_docs.model')
w_index = similarities.MatrixSimilarity.load(models_directory + "wikia_docs.index")
c_dict = corpora.Dictionary.load(models_directory + 'char4_docs.dict')
c_lda = models.ldamodel.LdaModel.load(models_directory + 'char4_docs.model')
c_index = similarities.MatrixSimilarity.load(models_directory + "char4_docs.index")
w_docs = []
c_docs = []
with open('parsed_docs_path.txt', 'r') as f:
    for line in f:
        w_docs.append(line.strip())
with open('parsed_char_path.txt', 'r') as f:
    for line in f:
        c_docs.append(line.strip())
session = {}


@app.route('/')
def hello():
    return render_template('search.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_request = request.form['request']
        entries = get_results(search_request, w_dict, w_lda, w_index, w_docs, c_dict, c_lda, c_index, c_docs)
        ids = list(map(lambda x: (x['character_id'], x['model']), entries))
        global session
        session['q'] = search_request
        session['r'] = ids
        return render_template('search_results.html', search_request=search_request, entries=entries)


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        selected = request.form.getlist('check')
        global session
        session['c'] = selected
        with open('clicks.json', 'r') as f:
            res = json.load(f)
            res.append(session)
        with open('clicks.json', 'w') as f:
            json.dump(res, f)
        session = {}
        return redirect(url_for('hello'))


@app.route('/page/<hub>/<wikia_id>/', defaults={'character_id': None})
@app.route('/page/<hub>/<wikia_id>/<character_id>/')
def page(hub, wikia_id, character_id):
    if character_id is None:
        filepath = 'static/hubs/{}/{}/{}.wiki'.format(hub, wikia_id, wikia_id)
    else:
        filepath = 'static/hubs/{}/{}/{}.txt'.format(hub, wikia_id, character_id)
    print(filepath)
    with app.open_resource(filepath, mode='r') as f:
        page_text = f.read().splitlines(keepends=False)
    return render_template('page.html', lines=page_text)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
