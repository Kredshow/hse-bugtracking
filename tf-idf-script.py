import nltk, math
import pandas as pd
from os import listdir


def get_tf_idf_matrix(path):
    file_names = listdir(path)
    result_frame = pd.DataFrame(columns=file_names)

    idx_in_file_names = 0
    for file_name in file_names:
        file = open(path + file_name, "r")
        data = file.read()
        tokenized_data = nltk.tokenize.WordPunctTokenizer().tokenize(data)

        words_counted = dict()
        for word in tokenized_data:
            if word in words_counted.keys():
                words_counted[word] = words_counted[word] + 1
            else:
                words_counted[word] = 1

        # Counts tf
        words_amount = len(tokenized_data)
        for word, count in words_counted.items():
            if word in result_frame.index:
                result_frame.loc[word][file_name] = count / words_amount
            else:
                vec_to_add = list(0 for i in range(len(file_names)))
                vec_to_add[idx_in_file_names] = count / words_amount
                result_frame.loc[word] = vec_to_add

        idx_in_file_names = idx_in_file_names + 1

    # Counts tf-idf matrix
    for index in result_frame.index:
        count_appears = 0
        for val in result_frame.loc[index]:
            if (val > 0):
                count_appears = count_appears + 1

        idf = math.log2(len(file_names) / count_appears)
        for column in result_frame.columns:
            result_frame.loc[index][column] = result_frame.loc[index][column] * idf


    return result_frame




