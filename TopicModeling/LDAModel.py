from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer
from stop_words import get_stop_words
import os

from gensim import corpora, models, similarities

docs_directory = 'FrontEnd/static/hubs/'
models_directory = 'TopicModels/'
doc_set = os.listdir(docs_directory)
tokenizer = RegexpTokenizer(r'[a-z]+')
stop_words = get_stop_words('en')
stemmer = SnowballStemmer('english')
num_topics = 200
num_words = 10


def parse_doc(path):
    tokens = []
    with open(path, 'r') as f:
        new_path = path.replace('.txt', '.p')
        if os.path.isfile(new_path):
           return
        for line in f:
            line = line.strip().lower()
            raw_tokens = tokenizer.tokenize(line)
            stopped_tokens = [i for i in raw_tokens if (not i in stop_words) and (len(i) > 2)]
            stemmed_tokens = [stemmer.stem(i) for i in stopped_tokens]
            tokens += stemmed_tokens
        print(new_path)
        with open(new_path, 'w') as p:
            print(' '.join(tokens), file=p)


def get_docs_path(s):
    docs_path = []
    for path, subdirs, files in os.walk(docs_directory):
        for name in files:
            docs_path.append(os.path.join(path, name))
    return list(filter(lambda path: path.endswith(s), docs_path))


if __name__ == "__main__":
    # print('start')
    # docs_path = get_docs_path('.txt')
    # print(len(docs_path))
    #
    #
    # for path in docs_path:
    #     parse_doc(path)
    # print('end of parsing')


    texts = []
    parsed_docs = get_docs_path('.p')
    for path in parsed_docs:
        with open(path, 'r') as f:
            tokens = []
            for line in f:
                tokens += line.split()
            texts.append(tokens)

    with open('parsed_char_path.txt', 'w') as f:
        for path in parsed_docs:
            print(path, file=f)
    print('end docs path')


    print('dict')
    # dictionary creation
    dictionary = corpora.Dictionary(texts)
    print(dictionary)
    dictionary.filter_extremes(no_below=5, no_above=0.2)
    dictionary.compactify()
    print(dictionary)
    dictionary.save(models_directory+'char_docs.dict')

    print('corp')
    # corpus creation
    corpus = [dictionary.doc2bow(text) for text in texts]
    corpora.MmCorpus.serialize(models_directory+'char_docs.mm', corpus)

    print('lda')
    # LDA_model creation
    ldamodel = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary)
    ldamodel.save(models_directory+'char_docs.model')

    index = similarities.MatrixSimilarity(ldamodel[corpus])
    index.save(models_directory + "char_docs.index")

    # generated topics
    topics = ldamodel.print_topics(num_topics=num_topics, num_words=num_words)
    print(*topics, sep='\r\n')
    with open(models_directory+'char_topics.txt', 'w') as f:
        for topic in topics:
            print(str(topic), file=f)




