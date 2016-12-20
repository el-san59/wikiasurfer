from elasticsearch import Elasticsearch
import os
import json
import random

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
char_index = 'char'
wikia_index = 'wikia'


def find_query(query, index):
    q = es.search(index=index, body={
        "query": {
            "bool": {
                "should": {
                    "match": {
                        "title": {
                            "query": query,
                            "fuzziness": 4,
                            "prefix_length": 2
                        }
                    }
                }
            }
        }
    })
    return q['hits']['hits']


def find_similar(ids, unlike_words, index):
    like = [{"_index": index, "_id": id} for id in ids]
    q = es.search(index=index, body={
        "query": {
            "more_like_this": {
                "fields" : ["page_text"],
                "like" : like,
                "unlike": unlike_words
            }
        }
    })
    return q['hits']['hits']


def get_results_for_wikia_ES(wikia):
    print('get_results_for_wikia_ES')
    id = wikia['_id']
    results = find_similar([id],'', wikia_index)
    return get_wiki_entries(results)


def get_results_for_wikia_ES_AND(wikias):
    print('get_results_for_char_ES_AND')
    ids = [wikia['_id'] for wikia in wikias]
    results = find_similar(ids, '', wikia_index)
    return get_wiki_entries(results)


def get_results_for_wikia_ES_OR(wikias):
    print('get_results_for_wikia_ES_OR')
    ids = [wikia['_id'] for wikia in wikias]
    results = []
    for id in ids:
        results += find_similar([id], '', wikia_index)
    results = sorted(results, key=lambda x: -x['_score'])
    for r in results:
        print(r['_score'], r['_source']['name_wiki'])
    return get_char_entries(results[:10])


def get_wiki_entries(results):
    entries = []
    for item in results:
        path = 'static/hubs/' + item['_source']['hub'] + '/' + item['_id']
        text = ''
        if os.path.exists('{0}/{1}.wiki'.format(path, item['_id'])):
            with open('{0}/{1}.wiki'.format(path, item['_id']), 'r') as f:
                for line in f:
                    text = line
                    break
        images = []
        dirs = [dI for dI in os.listdir(path) if os.path.isdir(os.path.join(path, dI))]
        for dir in dirs:
            im = os.listdir(os.path.join(path, dir))
            for i in im:
                images.append(os.path.join(path.replace('static/', ''), dir, i))
        entry = dict(hub=item['_source']['hub'], wikia_id=item['_id'], character_id=None, title=item['_source']['title'],
                     text=text, model='ES', score=item['_score'], images=images[:4])
        entries.append(entry)
    return entries


def get_unlike_words(ids_wiki):
    unlike_words = []
    for id in ids_wiki:
        g = es.search(index=char_index, body={
            "query": {
                "bool": {
                    "should": {
                        "match": {
                            "id_wiki": id
                        }
                    }
                }
            },
            "aggs": {
                "terms": {
                    "significant_terms": {
                        "field": "page_text",
                        "script_heuristic": {
                            "script": "_subset_freq"
                        },
                        "size": 1000000
                    }
                }
            }
        })
        num_char = g['aggregations']['terms']['doc_count']
        # print(len(g['aggregations']['terms']['buckets']))

        unlike = list(filter(lambda x: x['doc_count'] > 4 if num_char >= 4 else 0,
                             g['aggregations']['terms']['buckets']))
        # like = list(map(lambda x: x['key'],list(filter(lambda x: x['doc_count'] <= 4,
        #                      g['aggregations']['terms']['buckets']))))
        unlike_words += list(map(lambda x: x['key'], unlike))
        # print(len(unlike_words))
        # print(like)
    return ' '.join(unlike_words)


def get_results_for_char_ES(char):
    print('get_results_for_char_ES')
    id = char['_id']
    id_wiki = char['_source']['id_wiki']
    unlike_words = get_unlike_words([id_wiki])
    results = find_similar([id], unlike_words, char_index)
    for r in results:
        print(r['_score'], r['_source']['name_wiki'])
    entries = get_char_entries(results)
    return entries

def get_results_for_char_ES_AND(chars):
    print('get_results_for_char_ES_AND')
    ids = [char['_id'] for char in chars]
    ids_wiki = set([char['_source']['id_wiki'] for char in chars])
    print(ids_wiki)
    unlike_words = get_unlike_words(ids_wiki)
    results = find_similar(ids, unlike_words, char_index)
    return get_char_entries(results)


def get_results_for_char_ES_OR(chars):
    print('get_results_for_char_ES_OR')
    ids = [char['_id'] for char in chars]
    ids_wiki = set([char['_source']['id_wiki'] for char in chars])
    results = []
    for id, id_wiki in zip(ids, ids_wiki):
        results += find_similar([id], get_unlike_words([id_wiki]), char_index)
    results = sorted(results, key=lambda x: -x['_score'])
    for r in results:
        print(r['_score'], r['_source']['name_wiki'])
    return get_char_entries(results[:10])


def get_char_entries(results):
    entries = []
    for item in results:
        path = 'static/hubs/' + item['_source']['hub'] + '/' + item['_source']['id_wiki']
        text = ''
        i = 0
        with open('{0}/{1}.txt'.format(path, item['_source']['id_char']), 'r') as f:
            for line in f:
                text = line[:200]
                if i == 1:
                    break
                i += 1
        images = []
        if os.path.exists('{0}/{1}'.format(path, item['_source']['id_char'])):
            ims = os.listdir('{0}/{1}'.format(path, item['_source']['id_char']))
            for i in ims:
                images.append('{0}/{1}/{2}'.format(path.replace('static/', ''), item['_source']['id_char'], i))
        entry = dict(hub=item['_source']['hub'], wikia_id=item['_source']['id_wiki'], character_id=item['_source']['id_char'],
                     title='{0} ({1})'.format(item['_source']['title'], item['_source']['name_wiki']),
                     text=text, model='ES', score=item['_score'], images=images[:4])
        entries.append(entry)
    return entries


def get_results_for_wikia_LDA(wikia, dictionary, lda, index, docs):
    print('get_results_for_wikia_LDA')
    text_stem = wikia['_source']['page_text']
    vec_bow = dictionary.doc2bow(text_stem.split())
    vec_lda = lda[vec_bow]
    sims = index[vec_lda]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    sims = sims[:10]
    entries = []
    for s in sims:
        with open(docs[s[0]].replace('.pwiki', '.json').replace('./', 'static/'), 'r') as f:
            info = json.load(f)

        title = info['title']
        doc_wiki = docs[s[0]].replace('.pwiki', '.wiki').replace('./', 'static/')
        if os.path.exists(doc_wiki):
            with open(doc_wiki, 'r') as f:
                for line in f:
                    text = line
                    break
        images = []
        path = 'static/hubs/{0}/{1}'.format(info['hub'], info['id'])
        dirs = [dI for dI in os.listdir(path) if os.path.isdir(os.path.join(path, dI))]
        for dir in dirs:
            im = os.listdir(os.path.join(path, dir))
            for i in im:
                images.append(os.path.join(path.replace('static/', ''), dir, i))
        entry = dict(hub=info['hub'], wikia_id=info['id'], character_id=None, title=title,
                     text=text, model='LDA', score=s[1], images=images[:4])
        entries.append(entry)
    return entries


def get_results_for_char_LDA(char, dictionary, lda, index, docs):
    print('get_results_for_char_LDA')
    text_stem = char['_source']['page_text']
    vec_bow = dictionary.doc2bow(text_stem.split())
    vec_lda = lda[vec_bow]
    sims = index[vec_lda]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    sims = sims[:10]
    for s in sims:
        print(s)
    entries = []
    for s in sims:
        _, _, _, hub, wikia, char = docs[s[0]].split('/')
        char = int(char.replace('.p', ''))
        with open('static/hubs/{0}/{1}/{1}.json'.format(hub, wikia), 'r') as f:
            info = json.load(f)
        with open('static/hubs/{0}/{1}/{2}.txt'.format(hub, wikia, char), 'r') as f:
            i=0
            for line in f:
                if i==0:
                    title = line
                if i == 1:
                    text = line[:200]
                if i == 2:
                    break
                i+=1
        images = []
        path = 'static/hubs/{0}/{1}/{2}'.format(hub, wikia,char)
        if os.path.exists(path):
            ims = os.listdir(path)
            for i in ims:
                images.append(os.path.join(path.replace('static/', ''), i))
        entry = dict(hub=hub, wikia_id=wikia, character_id=char, title='{0} ({1})'.format(title, info['title']),
                     text=text, model='LDA', score=s[1], images=images[:4])
        entries.append(entry)
    return entries


def char_or_wiki(res_wiki, res_char):
    if not res_char:
        if not res_wiki:
            return None
        else:
            return 'w'
    else:
        if not res_wiki:
            return 'c'
        else:
            if res_wiki[0]['_score'] > res_char[0]['_score']:
                return 'w'
            else:
                return 'c'


def get_results_ES(query):
    if 'AND' in query:
        names = [x.strip() for x in query.split('AND')]
        # print(names)
        res_wiki = [find_query(name, wikia_index) for name in names]
        res_char = [find_query(name, char_index) for name in names]
        if char_or_wiki(res_wiki[0], res_char[0]) == 'w':
            res_wiki = [x[0] for x in res_wiki]
            # print(res_wiki)
            return get_results_for_wikia_ES_AND(res_wiki)
        else:
            res_char = [x[0] for x in res_char]
            # print(res_char)
            return get_results_for_char_ES_AND(res_char)

    if 'OR' in query:
        names = [x.strip() for x in query.split('OR')]
        res_wiki = [find_query(name, wikia_index) for name in names]
        res_char = [find_query(name, char_index) for name in names]
        if char_or_wiki(res_wiki[0], res_char[0]) == 'w':
            res_wiki = [x[0] for x in res_wiki]
            return get_results_for_wikia_ES_OR(res_wiki)
        else:
            res_char = [x[0] for x in res_char]
            return get_results_for_char_ES_OR(res_char)

    else:
        res_wiki = find_query(query, wikia_index)
        res_char = find_query(query, char_index)
        if char_or_wiki(res_wiki, res_char) == 'w':
            return get_results_for_wikia_ES(res_wiki[0])
        if char_or_wiki(res_wiki, res_char) == 'c':
            return get_results_for_char_ES(res_char[0])
        else:
            return None


def get_results_LDA(query, w_dict, w_lda, w_index, w_docs, c_dict, c_lda, c_index, c_docs):
    res_wiki = find_query(query, wikia_index)
    res_char = find_query(query, char_index)
    if char_or_wiki(res_wiki, res_char) == 'w':
        return get_results_for_wikia_LDA(res_wiki[0], w_dict, w_lda, w_index, w_docs)
    if char_or_wiki(res_wiki, res_char) == 'c':
        return get_results_for_char_LDA(res_char[0], c_dict, c_lda, c_index, c_docs)
    else:
        return None


def get_results(query, w_dict, w_lda, w_index, w_docs, c_dict, c_lda, c_index, c_docs):
    if 'AND' in query:
        names = [x.strip() for x in query.split('AND')]
        # print(names)
        res_wiki = [find_query(name, wikia_index) for name in names]
        res_char = [find_query(name, char_index) for name in names]
        if char_or_wiki(res_wiki[0], res_char[0]) == 'w':
            res_wiki = [x[0] for x in res_wiki]
            # print(res_wiki)
            return get_results_for_wikia_ES_AND(res_wiki)
        else:
            res_char = [x[0] for x in res_char]
            # print(res_char)
            return get_results_for_char_ES_AND(res_char)

    if 'OR' in query:
        names = [x.strip() for x in query.split('OR')]
        res_wiki = [find_query(name, wikia_index) for name in names]
        res_char = [find_query(name, char_index) for name in names]
        if char_or_wiki(res_wiki[0], res_char[0]) == 'w':
            res_wiki = [x[0] for x in res_wiki]
            return get_results_for_wikia_ES_OR(res_wiki)
        else:
            res_char = [x[0] for x in res_char]
            return get_results_for_char_ES_OR(res_char)

    else:
        res_wiki = find_query(query, wikia_index)
        res_char = find_query(query, char_index)
        if char_or_wiki(res_wiki, res_char) == 'w':
            print(res_wiki[0]['_source']['title'])
            ES_results = get_results_for_wikia_ES(res_wiki[0])
            LDA_results = get_results_for_wikia_LDA(res_wiki[0], w_dict, w_lda, w_index, w_docs)
        elif char_or_wiki(res_wiki, res_char) == 'c':
            print(res_char[0]['_source']['title'])
            # with open('static/hubs/{0}/{1}/{2}.txt'.format(res_char[0]['_source']['hub'],
            #                                                              res_char[0]['_source']['id_wiki'],
            #                                                              res_char[0]['_source']['id_char']), 'r') as f:
            #     for line in f:
            #         print(line)
            ES_results = get_results_for_char_ES(res_char[0])
            LDA_results = get_results_for_char_LDA(res_char[0], c_dict, c_lda, c_index, c_docs)
        else:
            return None
        # entries = interleaving(ES_results, LDA_results, 0.5, 20)
        normalizer(ES_results, 0.3, 1)
        print('----------------')
        for res in ES_results:
            print(res['score'])
        normalizer(LDA_results, 0.7, 1)
        print('----------------')
        for res in LDA_results:
            print(res['score'])
        entries = merge_results(ES_results, LDA_results)

        for entry in entries:
            print(entry['score'], entry['model'], entry['title'])
        return entries


#z_score + w_resourse
def normalizer(results, w_resourse, l):
    min_score = results[-1]['score']
    print(min_score)
    for i in range(len(results)):
        results[i]['score'] -= min_score
    sum_score = 0
    for i in range(len(results)):
        sum_score += results[i]['score']
    print(sum_score)
    for i in range(len(results)):
        results[i]['score'] = (results[i]['score'] / sum_score) * (1+l*w_resourse)


def merge_results(ES_results, LDA_results):
    entries = []
    while ES_results and LDA_results and len(entries)<10:
        if ES_results[0]['score'] >= LDA_results[0]['score']:
            entries.append(ES_results[0])
            LDA_results = [x for x in LDA_results if x['title'] != ES_results[0]['title']]
            ES_results.pop(0)
        else:
            entries.append(LDA_results[0])
            ES_results = [x for x in ES_results if x['title'] != LDA_results[0]['title']]
            LDA_results.pop(0)
    if len(entries) < 10:
        if ES_results:
            entries += ES_results
        else:
            entries += LDA_results
    return entries[:10]





def interleaving(ES_results, LDA_results, p, n):
    entries = []
    while len(entries) < n:
        if random.random() < p and ES_results:
            entries.append(ES_results[0])
            LDA_results = [x for x in LDA_results if x['title'] != ES_results[0]['title']]
            ES_results.pop(0)
        elif LDA_results:
            entries.append(LDA_results[0])
            ES_results = [x for x in ES_results if x['title'] != LDA_results[0]['title']]
            LDA_results.pop(0)
        else:
            break
    return entries

