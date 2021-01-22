from textwrap import dedent
from lxml import etree
import json
from argparse import Namespace
from unittest.mock import patch
import csv

import pytest

from stackoverflow_analytics import (
    load_xml_documents,
    build_word_popularity_index,
    ArgumentParser,
    callback_query,
    main,
    STOP_WORDS_FPATH,
)

QUERIES_FPATH = 'queries_sample.csv'
DATASET_TINY_XML = dedent("""\
    <row PostTypeId="1" CreationDate="2008-10-15" Score="1" Title="how linux linux?" />	
    <row PostTypeId="1" CreationDate="2008-10-15" Score="12" Title="How command work in Linux?" />
    <row PostTypeId="1" CreationDate="2009-10-15" Score="5" Title="How command work in Unix?" />	
    <row PostTypeId="1" CreationDate="2009-10-15" Score="-4" Title="How command work in Linux?" />	
    <row PostTypeId="2" CreationDate="2008-10-15" Score="12"/>\
""")
QUERIES_SAMPLE = [
    [2008, 2008, 2],
    [2008, 2008, 4],
    [2008, 2009, 3],
    [2010, 2012, 1]
]


@pytest.fixture()
def tiny_dataset_fio(tmpdir):
    dataset_fio = tmpdir.join("dataset.xml")
    dataset_fio.write(DATASET_TINY_XML)
    return dataset_fio


@pytest.fixture()
def queries_sample_fio(tmpdir):
    queries_fio = tmpdir.join("queries_sample.csv")
    with open(queries_fio, 'w', newline='') as f_in:
        writer = csv.writer(f_in, delimiter=',')
        for query in QUERIES_SAMPLE:
            writer.writerow(query)
    return queries_fio


def test_can_load_xml_documents(tiny_dataset_fio):
    documents = load_xml_documents(tiny_dataset_fio)
    etalon_documents = [
        etree.fromstring(
            '<row PostTypeId="1" CreationDate="2008-10-15" Score="1" Title="how linux linux?" />',
            etree.XMLParser()),
        etree.fromstring(
            '<row PostTypeId="1" CreationDate="2008-10-15" Score="12" Title="How command work in Linux?" />',
            etree.XMLParser()),
        etree.fromstring(
            '<row PostTypeId="1" CreationDate="2009-10-15" Score="5" Title="How command work in Unix?" />',
            etree.XMLParser()),
        etree.fromstring(
            '<row PostTypeId="1" CreationDate="2009-10-15" Score="-4" Title="How command work in Linux?" />',
            etree.XMLParser()),
        etree.fromstring(
            '<row PostTypeId="2" CreationDate="2008-10-15" Score="12"/>',
            etree.XMLParser()),
    ]
    assert len(etalon_documents) == len(documents), "load_xml_documents incorrectly loaded dataset"
    assert sum([0 if x.values() == y.values() else 1 for x, y in zip(etalon_documents, documents)]) == 0, (
        "load_xml_documents incorrectly loaded dataset"
    )


@pytest.mark.parametrize(
    "query, etalon_answer",
    [
        pytest.param(
            [2008, 2008, 2],
            json.dumps({"start": 2008, "end": 2008, "top": [["linux", 13], ["command", 12]]}),
            id="2008 top 2"
        ),
        pytest.param(
            [2008, 2008, 4],
            json.dumps({"start": 2008, "end": 2008, "top": [["linux", 13], ["command", 12], ["work", 12]]}),
            id="2008 top 4 - not enough data to answer"
        ),
        pytest.param(
            [2008, 2009, 3],
            json.dumps({"start": 2008, "end": 2009, "top": [["command", 13], ["work", 13], ["linux", 9]]}),
            id="2008/2009 top 3"
        ),
        pytest.param(
            [2010, 2012, 1],
            json.dumps({"start": 2010, "end": 2012, "top": []}),
            id="2010/2012 top 1 - not enough data to answer"
        ),

    ]
)
def test_query_word_popularity_index(tiny_dataset_fio, query, etalon_answer):
    documents = load_xml_documents(tiny_dataset_fio)
    tiny_word_popularity_index = build_word_popularity_index(documents)
    answer = tiny_word_popularity_index.query(*query)
    assert answer == etalon_answer, (
        f"Expected answer is {etalon_answer}, but got {answer}"
    )


def test_main_can_properly_ran_all_process(tiny_dataset_fio, queries_sample_fio, capsys, caplog):
    with patch.object(
            ArgumentParser,
            "parse_args",
            return_value=Namespace(
                dataset_fpath=tiny_dataset_fio,
                stop_words_fpath=STOP_WORDS_FPATH,
                queries_fpath=queries_sample_fio,
                callback=callback_query,
            )
    ):
        main()
    captured = capsys.readouterr()

    assert '["command", 13], ["work", 13], ["linux", 9]' in captured.out
    assert '' == captured.err, "service messages must no be in stderr"
