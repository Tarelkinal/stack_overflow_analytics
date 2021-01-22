# stack_overflow_analytics
The app provides a console interface for queries about the most popular topics fro discussion during the specified period for stackoverflow.com

## Repository content
stackoverflow_analytics.py - console interface implementation based on argparse module
test_stackoverflow_analytics.py - unit tests
logging.conf.yml - logger configuration
stop_words_in_koi8r.txt - stop words list
stackoverflow_posts_sample.xml - sample of input dataset

## Application functionality
Application provides the following interface:
- read the dataset in xml-lines format (encoding: utf-8)
- read stop words (encoding: koi8-r)
- displaying analytics on the screen
- logging system behavior to log files

$ python3 stackoverflow_analytics.py --questions /path/to/dataset/questions.xml --stop-words /path/to/stop_words_in_koi8r.txt --queries /path/to/quries.csv
