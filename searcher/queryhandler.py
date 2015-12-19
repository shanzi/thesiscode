#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import bz2
import argparse

import cPickle as pickle
from collections import Counter

__all__ = ('BoolQueryHandler', 'ConceptualGraphQueryHandler')


class QueryHandlerBase(object):
    def __init__(self, path):
        self._path = path
        self.loadindex()

    def loadindex(self):
        with bz2.BZ2File(self._path) as f:
            self._index = pickle.load(f)

    def query(self, kw):
        raise NotImplementedError()


class BoolQueryHandler(QueryHandlerBase):

    """This class handles queries by bool model"""

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


class ConceptualGraphQueryHandler(QueryHandlerBase):

    def query(self, graph):
        pass
