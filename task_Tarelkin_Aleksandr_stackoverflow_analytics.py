#!C:\Users\tarel\Anaconda3\envs\python_advanced\python.exe
"""Module for calculation words popularity score over Stackoverflow posts"""
import csv
import json
import logging
import logging.config
import re
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from collections import defaultdict

import yaml
from lxml import etree


STOP_WORDS_FPATH = 'stop_words_in_koi8r.txt'
LOGGING_CONFIG_YAML = 'logging.conf.yml'
APPLICATION_NAME = 'task_Tarelkin_Aleksandr_stackoverflow_analytics'


logger = logging.getLogger(APPLICATION_NAME)


class WordPopularityIndex:
    """
    Provide functionality to processing queries to stackoverflow word popularity index

    use WordPopularityIndex.query to find top words based on their popularity during period provided

    Attributes
    ----------
    word_popularity_index: keep word popularity index by years
    """
    def __init__(self, word_popularity_index: dict):
        """construct object of class with word popularity index built by years"""
        self.word_popularity_index = word_popularity_index

    def query(self, start_year: int, end_year: int, top_len: int):
        """
        Function to query word popularity index

        :param start_year: start year for considering period
        :param end_year: last year for considering period (included)
        :param top_len: number of top words based on score popularity
        :return: JSON of the form {
            "start": start_year,
            "end": end_year,
            "top": [["top_1_word": top_1_word_score], ..., ["top_n_word": top_n_word_score]]
        }
        """
        logger.debug('got query "%s,%s,%s"', repr(start_year), repr(end_year), repr(top_len))

        answer_dict = defaultdict(int)
        for year in range(start_year, end_year + 1):
            if year in self.word_popularity_index.keys():
                for word, score in self.word_popularity_index[year].items():
                    answer_dict[word] += score
        if len(answer_dict) < top_len:
            logger.warning(
                'not enough data to answer, found '
                'top_%s words out of top_%s for period "%s,%s"',
                len(answer_dict),
                top_len,
                start_year,
                end_year
            )
            top_len = len(answer_dict)
        answer_list = [[w, s] for w, s in answer_dict.items()]
        pre_sort = sorted(answer_list, key=lambda x: x[0])
        answer_list = sorted(pre_sort, key=lambda x: x[1], reverse=True)[:top_len]
        answer = json.dumps({"start": start_year, "end": end_year, "top": answer_list})

        return answer


def load_xml_documents(fpath: str) -> list:
    """Return list of etree objects"""
    with open(fpath, 'rb') as f_in:
        documents = [etree.fromstring(x.strip().decode(), etree.XMLParser()) for x in f_in.readlines()]

    return documents


def build_word_popularity_index(documents: list, stop_words_path=STOP_WORDS_FPATH) -> WordPopularityIndex:
    """
    Return WordPopularityIndex class object initialized with
    word popularity index built by years
    """
    word_popularity_index = defaultdict(lambda: defaultdict(int))

    with open(stop_words_path, 'r', encoding='koi8-r') as f_sw_in:
        stop_words_list = [x.strip() for x in f_sw_in.readlines()]

    for elem in documents:
        if elem.xpath('@PostTypeId')[0] == '2':
            continue
        score = int(elem.xpath('@Score')[0])
        year = int(elem.xpath('@CreationDate')[0][:4])
        words = re.findall(r'\w+', elem.xpath('@Title')[0].lower())
        for word in set(words):
            if word in stop_words_list:
                continue
            word_popularity_index[year][word] += score

    word_popularity_index_built = WordPopularityIndex(word_popularity_index)

    return word_popularity_index_built


def callback_query(dataset_fpath: str, stop_words_fpath: str, queries_fpath: str):
    """
    Process commands received from CLI
    """
    documents = load_xml_documents(dataset_fpath)
    word_popularity_index = build_word_popularity_index(documents, stop_words_fpath)

    logger.info('process XML dataset, ready to serve queries')

    queries_list = []
    with open(queries_fpath, 'r') as f_in:
        reader = csv.reader(f_in, delimiter=',')
        for row in reader:
            queries_list.append(list(map(int, row)))

    for query in queries_list:
        query_result = word_popularity_index.query(*query)
        print(f'{query_result}\n', file=sys.stdout)

    logger.info('finish processing queries')


def setup_parser(parser):
    parser.add_argument(
        "--questions", required=True, dest="dataset_fpath",
        help="path to stackoverflow dataset to load"
    )
    parser.add_argument(
        "--stop-words", required=True, dest="stop_words_fpath",
        help="path to stop words document in koi8-r encoding to exclude them from popularity index"
    )
    parser.add_argument(
        "--queries", required=True, dest="queries_fpath",
        help="path to queries to query them against popularity index"
    )
    parser.set_defaults(callback=callback_query)


def setup_logging():
    with open(LOGGING_CONFIG_YAML) as config_fin:
        logging.config.dictConfig(yaml.safe_load(config_fin))


def main():
    setup_logging()
    parser = ArgumentParser(
        prog="word-popularity-index",
        description="tool to build and query word-popularity index for stackoverflow dataset",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    setup_parser(parser)
    arguments = parser.parse_args()

    arguments.callback(
        arguments.dataset_fpath,
        arguments.stop_words_fpath,
        arguments.queries_fpath,
    )


if __name__ == "__main__":
    main()
