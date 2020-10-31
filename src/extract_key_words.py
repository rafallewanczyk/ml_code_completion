#!/usr/bin/env python
# This file goes through the data directory, looking for source files that
# match the input pattern, parses these files and extracts out key words from
# the files.
# Usage:
# ./extract_key_words.py -s <comma separated suffix list> -o <outfile>

import key_word_extractor as ke
import os
import argparse

def listparse(arg):
    return arg.split(',')

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--project',
                    help='project name')
parser.add_argument('-l', '--langs',
                    type=listparse,
                    help='languages to use as a comma separated list')
parser.add_argument('-n', '--num',
                    type=int,
                    default=2000,
                    help='how many keywords to extract')

args = parser.parse_args()

# root data directory
root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
root_data_dir = os.path.join(root_dir, 'data', args.project)
key_word_dir = os.path.join(root_dir, 'key_words')

if not os.path.exists(root_data_dir):
    raise ValueError('Project data directory %s doesn\'t exist' % root_data_dir)

if not os.path.exists(key_word_dir):
  os.makedirs(key_word_dir)

key_word_file = os.path.join(key_word_dir, args.project)

# number of keywords to extract
max_key_words=args.num
#percentile_key_words=95

# list of languages, corresponding file suffixes, a flag indicating whether
# to parse or skip, a list of data directories to read
#suffixes  = 'suffixes'
#parse     = 'parse'
#data_dirs = 'data_dirs'
#outfile   = 'outfile'
#languages = {
#    'h'      : { suffixes  : ['h'],
#                 parse     : False,
#                 data_dirs : [ root_data_dir ],
#                 outfile   : os.path.join(key_word_dir, "h")
#               },
#    'c'      : { suffixes  : ['h', 'c', 'cc', 'cpp'],
#                 parse     : True,
#                 data_dirs : [ root_data_dir ],
#                 outfile   : os.path.join(key_word_dir, "c")
#               },
#    'python' : { suffixes  : ['py'],
#                 parse     : False,
#                 data_dirs : [ root_data_dir ],
#                 outfile   : os.path.join(key_word_dir, "python")
#               }
#    }

# Extract key words and save them
print("Extracting key words for project %s ..." % args.project)
words = ke.FrequentWords(data_dirs=[root_data_dir], suffixes=args.langs,
                         max_key_words=max_key_words)
with open(key_word_file, 'w') as out:
  for key_word, count in words:
    out.write("%s %d\n" % (key_word, count))
print("Completed extracting key words for project %s" % args.project)
