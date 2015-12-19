#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import bz2
import argparse

import cPickle as pickle
from collections import Counter


class BoolQueryHandler(object):

    """This class handles queries by bool model"""

    def __init__(self, path):
        self._path = path
        self.loadindex()

    def loadindex(self):
        with bz2.BZ2File(self._path) as f:
            self._index = pickle.load(f)

    def getquestion(self, qres):
        qid, score = qres
        question = self._index['questions'][qid]
        return (question, qid, score)

    def query(self, words):
        counter = Counter()
        wordssection = [self._index['words'][w] for w in words]
        for section in wordssection:
            for qid in section: counter.update({qid: 1})
        return map(self.getquestion, counter.most_common(20))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help="Path to index file")
    args = parser.parse_args()
    if args.path:
        queryHandler = BoolQueryHandler(args.path)
        while True:
            keywords = filter(None, raw_input('> ').decode('utf8').split())
            print queryHandler.query(keywords)
