import requests
from elasticsearch import Elasticsearch
import os
import json

docs_directory = 'FrontEnd/static/hubs/'


def get_docs_path(s):
    docs_path = []
    for path, subdirs, files in os.walk(docs_directory):
        for name in files:
            docs_path.append(os.path.join(path, name))
    return list(filter(lambda path: s in path, docs_path))


es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

r = requests.get('http://localhost:9200')
print(r.content)


def wikia_index():
    docs_path = get_docs_path('.wiki.json')
    # print(docs_path)

    for path in docs_path:
        with open(path, 'r') as f:
            doc = json.load(f)

    es.index(index='wikia',
         doc_type=doc['tag'],
         id=doc['id'],
         body={
             'title': doc['title'],
             'page_text': doc['text'],
             'url': doc['url'],
             'hub': doc['hub'],
             'id': doc['id']
         })


docs_path = get_docs_path('.char.json')
print(len(docs_path))

for path in docs_path:
    with open(path, 'r') as f:
        doc = json.load(f)

    es.index(index='char',
             doc_type=doc['tag'],
             id=doc['id'],
             body={
                 'title': doc['title'],
                 'page_text': doc['text'],
                 'url': doc['url'],
                 'hub': doc['hub'],
                 'id': doc['id'],
                 'id_wiki': doc['id_wiki'],
                 'id_char': doc['id_char'],
                 'name_wiki': doc['name_wiki']
             })
