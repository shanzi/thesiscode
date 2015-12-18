#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import bz2
import glob
import json
import jieba
import logging
import argparse
import coloredlogs
import cPickle as pickle

from collections import defaultdict

SYM = re.compile(ur'[^\u4e00-\u9fa5]+')
coloredlogs.install()


class Indexer(object):

    """Indexer index questions and persist them for further usage"""

    def __init__(self, path):
        self._path = path
        self._words = defaultdict(set)
        self._questions = dict()
        self._topics = dict()

    @property
    def filenames(self):
        return glob.glob(os.path.join(self._path, '*.json'))

    def loadtopic(self, topic):
        topicid = topic['id']
        topicname = topic['name']
        logging.info('Loading topic [%s (%d)]' % (topicname, topicid))
        self._topics[topicid] = topicname
        for question in topic['questions']:
            qid = question['id']
            qtitle = question['title']

            subtopic = question['subtopic']
            self._topics[subtopic['id']] = subtopic['title']

            self._questions[qid] = dict(
                title=qtitle,
                topic=set([topicid, subtopic['id']])
            )

    def loaddata(self):
        logging.info('Loading data')
        for filename in self.filenames:
            with open(filename) as f:
                topic = json.load(f)
                self.loadtopic(topic)

    def indexquestion(self, qid, question):
        title = SYM.sub(' ', question['title'])
        fragments = filter(None, jieba.cut_for_search(title))
        for fragment in fragments:
            self._words[fragment].add(qid)

    def index(self):
        self.loaddata()
        logging.info('Indexing questions')
        for qid, question in self._questions.iteritems():
            self.indexquestion(qid, question)

    def persist(self, outfilepath):
        data = dict(
            words=self._words,
            topics=self._topics,
            questions=self._questions
        )
        logging.info('Persisting to file: %s' % outfilepath)
        with bz2.BZ2File(outfilepath, 'w') as f:
            pickle.dump(data, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("indir", help="The path of directory to read in raw data files")
    parser.add_argument("outfile", help="The path of file to save indexed data")
    args = parser.parse_args()
    if args.indir and args.outfile:
        indexer = Indexer(args.indir)
        indexer.index()
        indexer.persist(args.outfile)
