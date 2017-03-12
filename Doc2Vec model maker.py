import multiprocessing
import codecs
import os
import nltk
from gensim.models import doc2vec
from nltk.tokenize import RegexpTokenizer
import sklearn.manifold
import matplotlib.pyplot as plt

class Doc2VecModel:
    class _DatabaseIterable:
        def __init__(self, path):
            self.path = path + "database/"
            self.list_dir = os.listdir(self.path)
            self.dir_position = -1
            self.list_docs = list()
            self.docs_position = 0
            self.find_first_non_empty_dir()
            self.tokenizer = RegexpTokenizer('\w+|\$[\d\.]+|\S+')

        def __iter__(self):
            return self

        def __next__(self):
            if self.docs_position == len(self.list_docs):
                self.find_first_non_empty_dir()

            if self.dir_position >= len(self.list_dir):
                raise StopIteration

            if os.path.isdir(self.path +
                    self.list_dir[self.dir_position] + "/"
                    + self.list_docs[self.docs_position]):
                self.docs_position += 1

            if self.docs_position == len(self.list_docs):
                self.find_first_non_empty_dir()

            if self.dir_position >= len(self.list_dir):
                raise StopIteration

            report_file = open(self.path + self.list_dir[self.dir_position]
                                 + "/" + self.list_docs[self.docs_position])
            words = self.tokenizer.tokenize(report_file.read())
            tag = self.list_docs[self.docs_position]
            tag = tag[0:len(tag) - 4]
            self.docs_position += 1
            return doc2vec.TaggedDocument(words=words, tags=[tag])

        def find_first_non_empty_dir(self):
            self.dir_position += 1
            while (self.dir_position < len(self.list_dir)):
                self.list_docs = os.listdir(self.path + self.list_dir[self.dir_position])
                if len(self.list_docs) > 1:
                    self.docs_position = 0
                    break
                else:
                    self.dir_position += 1

    path = ""
    model = doc2vec.Doc2Vec()


    def __init__(self, set_path):
        self.path = set_path
        if os.path.exists(self.path + "saved_model.pkl"):
            self.model = doc2vec.Doc2Vec.load(self.path + "saved_model.pkl")
        else:
            self.model = doc2vec.Doc2Vec(size=100, window=8, min_count=5,
                                         workers=multiprocessing.cpu_count())


    def train_model_on_database(self):
        iterable = self._DatabaseIterable(self.path)
        self.model = doc2vec.Doc2Vec(documents=iterable, size=100, window=8,
                                     min_count=5, workers=multiprocessing.cpu_count())

        iterable = self._DatabaseIterable(self.path)
        for epoch in range(10):
            self.model.train(iterable)
            self.model.alpha -= 0.002
            self.model.min_alpha = self.model.alpha

        self.model.delete_temporary_training_data()
        self.model.save("saved_model.pkl")


    def similar(self):
        for name in self.model.docvecs.doctags:
            print(name)

    def visualize_dataset(self):
        types = dict()
        list_date = os.listdir(self.path + "database")
        for date in list_date:
            list_files = os.listdir(self.path + "database/" + date + "/Additional")
            for file_name in list_files:
                info_file = open(self.path + "database/" + date + "/Additional/" + file_name)
                info_file.readline()

                file_name = file_name[0:len(file_name) - 4]
                types[file_name] = info_file.readline().strip()

        colors = {'Bug': 'red', 'Task':'blue', 'Improvement':'lightgreen', 'Sub-task':'purple'}
        tsne = sklearn.manifold.TSNE(n_components=2, random_state=0)
        reduced_vectors = tsne.fit_transform(self.model.docvecs)

        plt.figure()
        i = 0
        for name in self.model.docvecs.doctags:
            if types[name] in colors.keys():
                col = colors[types[name]]
            else:
                col = 'cyan'
            plt.scatter(x=reduced_vectors[i][0], y=reduced_vectors[i][1],
                        c=col, label=name)
            i += 1

        plt.xlabel('X in t-SNE')
        plt.ylabel('Y in t-SNE')
        plt.legend(loc='upper left')
        plt.title('t-SNE visualization of test data')
        plt.show()




path = "/home/kredshow/PycharmProjects/Bug-tracking/"

if __name__ == "__main__":
    obj = Doc2VecModel(path)
    obj.visualize_dataset()
    #obj.train_model_on_database()
    #obj.similar()