from gensim import corpora, models, similarities
import os
import json

docs_directory = './hubs/'
models_directory = 'TopicModels/'


def get_docs_path(s):
    docs_path = []
    for path, subdirs, files in os.walk(docs_directory):
        for name in files:
            docs_path.append(os.path.join(path, name))
    return list(filter(lambda path: s in path, docs_path))

dictionary = corpora.Dictionary.load(models_directory+'wikia_docs.dict')
corpus = corpora.MmCorpus(models_directory+'wikia_docs.mm')
lda = models.ldamodel.LdaModel.load(models_directory+'wikia_docs.model')
index = similarities.MatrixSimilarity.load(models_directory+"wikia_docs.index")
print('load done')

docname = "hubs/Movies/759/759.pwiki"
doc = open(docname, 'r').read()
vec_bow = dictionary.doc2bow(doc.lower().split())
vec_lda = lda[vec_bow]

print('begin sims')
sims = index[vec_lda]
sims = sorted(enumerate(sims), key=lambda item: -item[1])
sims = sims[:10]
print(sims)

# docs_path = get_docs_path('.pwiki')
# with open('parsed_docs_path.txt', 'w') as f:
#     for path in docs_path:
#         print(path, file=f)
# print('end docs path')

docs_path = []
with open('parsed_docs_path.txt', 'r') as f:
    for line in f:
        docs_path.append(line.strip())


with open('similar_docs.txt', 'w') as f:
    print(docname, file=f)
    print('is similar to:', file=f)
    for s in sims:
        with open(docs_path[s[0]].replace('.pwiki', '.json'), 'r') as d:
            info = json.load(d)
            print(info)
            print('{3} - {0} - {1} - {2}'.format(info['title'], info['url'], info['hub'], s[1]), file=f)


