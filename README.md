# stack_overflow_analytics
The app provides a console interface for queries about the most popular topics fro discussion during the specified period for stackoverflow.com

## Repository content
- stackoverflow_analytics.py - console interface implementation based on argparse module
- test_stackoverflow_analytics.py - unit tests
- logging.conf.yml - logger configuration
- stop_words_in_koi8r.txt - stop words list
- stackoverflow_posts_sample.xml - sample of input dataset
- test.csv - sample of query

## Application functionality
Application provides the following interface:
- read the dataset in xml-lines format (encoding: utf-8)
- read stop words (encoding: koi8-r)
- displaying analytics on the screen
- logging system behavior to log files

### Command example
$ python3 stackoverflow_analytics.py --questions /path/to/dataset/questions.xml --stop-words /path/to/stop_words_in_koi8r.txt --queries /path/to/quries.csv

### Output format
json(dict)

### Output example
{“start”: start_year, “end”: end_year, “top”: [[“top_1_word”,
top_1_word_score), [“top_2_word”, top_2_word_score], ..., [“top_N_word”,
top_N_word_score]]}

### What is the most popular topics
The popularity value of a word is the sum of all the ratings of questions in the title of which the word has appeared 1 or more times.

