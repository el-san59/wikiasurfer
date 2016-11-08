from elasticsearch import Elasticsearch
import os
import json

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

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


def find_similar(id, index):
    q = es.search(index=index, body={
        "query": {
            "more_like_this": {
                "fields" : ["page_text"],
                "like" : {
                    "_index" : index,
                    "_id" : id
                }
            }
        }
    })
    return q['hits']['hits']


def get_results_for_wikia(wikia):
    print('get_results_for_char_ES')
    id = wikia['_id']
    results = find_similar(id, 'wikia')
    entries = []
    for item in results:
        path = 'static/hubs/'+ item['_source']['hub'] + '/' + item['_id']
        text = ''
        if os.path.exists('{0}/{1}.wiki'.format(path, item['_id'])):
            with open('{0}/{1}.wiki'.format(path, item['_id']), 'r') as f:
                for line in f:
                    text = line
                    break
        images = []
        dirs = [dI for dI in os.listdir(path) if os.path.isdir(os.path.join(path, dI))]
        # print(dirs)
        for dir in dirs:
            im = os.listdir(os.path.join(path, dir))
            for i in im:
                images.append(os.path.join(path.replace('static/', ''), dir, i))
        # print(images)

        entry = dict(ref=item['_source']['url'], title=item['_source']['title'],
        text=text, images=images[:4])
        entries.append(entry)
    # print(entries)
    return entries

def get_results_for_char(char):
    print('get_results_for_char_ES')
    id = char['_id']
    results = find_similar(id, 'char')
    entries = []
    for item in results:
        path = 'static/hubs/' + item['_source']['hub'] + '/' + item['_source']['id_wiki']
        text = ''
        i=0
        with open('{0}/{1}.txt'.format(path, item['_source']['id_char']), 'r') as f:
            for line in f:
                text = line
                if i == 1:
                    break
                i += 1
        images = []
        if os.path.exists('{0}/{1}'.format(path, item['_source']['id_char'])):
            ims = os.listdir('{0}/{1}'.format(path, item['_source']['id_char']))
            for i in ims:
                images.append('{0}/{1}/{2}'.format(path.replace('static/', ''), item['_source']['id_char'], i))
        # print(images)

        entry = dict(ref=item['_source']['url'],
                     title='{0} ({1})'.format(item['_source']['title'],item['_source']['name_wiki']),
                     text=text, images=images[:4])
        entries.append(entry)
    # print(entries)
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
        ref = info['url']
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
        # print(dirs)
        for dir in dirs:
            im = os.listdir(os.path.join(path, dir))
            for i in im:
                images.append(os.path.join(path.replace('static/', ''), dir, i))
        # print(images)

        entry = dict(ref=ref, title=title,
                     text=text, images=images[:4])
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
    entries = []
    for s in sims:
        _, _, _, hub, wikia, char = docs[s[0]].split('/')
        char = char.replace('.p', '')
        with open('static/hubs/{0}/{1}/{1}.json'.format(hub, wikia), 'r') as f:
            info = json.load(f)
        ref = info['url']
        with open('static/hubs/{0}/{1}/{2}.txt'.format(hub, wikia, char), 'r') as f:
            i=0
            for line in f:
                if i==0:
                    title = line
                if i == 1:
                    text = line
                if i == 2:
                    break
                i+=1
        images = []
        path = 'static/hubs/{0}/{1}/{2}'.format(hub, wikia,char)
        if os.path.exists(path):
            ims = os.listdir(path)
            for i in ims:
                images.append(os.path.join(path.replace('static/', ''), i))
            # print(images)

        entry = dict(ref=ref, title='{0} ({1})'.format(title, info['title']),
                     text=text, images=images[:4])
        entries.append(entry)
    return entries


def get_results_ES(query):
    res_wiki = find_query(query, 'wikia')
    res_char = find_query(query, 'char')
    if not res_char:
        if not res_wiki:
            return None
        else:
            return get_results_for_wikia(res_wiki[0])
    else:
        if not res_wiki:
            return get_results_for_char(res_char[0])
        else:
            if res_wiki[0]['_score'] > res_char[0]['_score']:
                return get_results_for_wikia(res_wiki[0])
            else:
                return get_results_for_char(res_char[0])


def get_results_LDA(query, w_dict, w_lda, w_index, w_docs, c_dict, c_lda, c_index, c_docs):
    res_wiki = find_query(query, 'wikia')
    res_char = find_query(query, 'char')
    if not res_char:
        if not res_wiki:
            return None
        else:
            return get_results_for_wikia_LDA(res_wiki[0], w_dict, w_lda, w_index, w_docs)
    else:
        if not res_wiki:
            return get_results_for_char_LDA(res_char[0], c_dict, c_lda, c_index, c_docs)
        else:
            if res_wiki[0]['_score'] > res_char[0]['_score']:
                return get_results_for_wikia_LDA(res_wiki[0], w_dict, w_lda, w_index, w_docs)
            else:
                return get_results_for_char_LDA(res_char[0], c_dict, c_lda, c_index, c_docs)
