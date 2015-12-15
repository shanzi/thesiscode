#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json
import glob
import logging
import argparse
import coloredlogs

from collections import Counter

coloredlogs.install()


SYM = re.compile(ur'[^\u4e00-\u9fa5]')
QSYM = re.compile(ur'[\?\uff1f]')
SSYM = re.compile(ur'[\.\u3002]')


class StatisticRunner(object):

    """Run statistic for data files"""

    def __init__(self, path):
        self._path = path
        self._qid_set = set()
        self._tid_set = set()
        self._length_counter = Counter()
        self._subsentence_counter = Counter()
        self._qs_counter = Counter()

    @property
    def filenames(self):
        return glob.glob(os.path.join(self._path, '*.json'))

    def contents(self, filename):
        with open(filename) as f:
            return json.load(f)

    def countlength(self, text):
        l = len(SYM.sub('', text))
        self._length_counter.update({l: 1})

    def countsubsentence(self, text):
        l = len(filter(None, SYM.split(text)))
        self._subsentence_counter.update({l: 1})

    def countqs(self, text):
        if not QSYM.search(text):
            self._qs_counter.update({'NOQ': 1})
        elif not SSYM.search(text):
            self._qs_counter.update({'NOS': 1})
        else:
            self._qs_counter.update({'MIX': 1})

    def process_topic(self, contents):
        logging.info("Processing topic: %s (%d)" % (contents['name'], contents['id']))
        self._tid_set.add(contents['id'])
        questions = contents['questions']
        for q in questions:
            qid = q['id']
            if qid in self._qid_set: continue

            self._qid_set.add(qid)
            subtopic = q['subtopic']
            self._tid_set.add(subtopic['id'])

            self.countlength(q['title'])
            self.countsubsentence(q['title'])
            self.countqs(q['title'])

    def run(self):
        for filename in self.filenames:
            self.process_topic(self.contents(filename))

    def summary(self):
        logging.info("Printing summary")
        print "Distinect topics: %d" % len(self._tid_set)
        print "Distinct questions: %d" % len(self._qid_set)
        print
        print "Length distribution:"
        lc = self._length_counter
        for i in range(50):
            print "%d: %d" % (i, (lc[i] if i in lc else 0))
        print
        print "Subsentence count distribution:"
        sc = self._subsentence_counter
        for i in sorted(sc.keys()):
            print "%d: %d" % (i, sc[i])
        print
        print "QS distribution:"
        qsc = self._qs_counter
        for k in ('NOQ', 'NOS', 'MIX'):
            print "%s: %d" % (k, (qsc[k] if k in qsc else 0))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="The path of directory that contains all data files")
    args = parser.parse_args()
    if args.path:
        s = StatisticRunner(args.path)
        s.run()
        s.summary()
