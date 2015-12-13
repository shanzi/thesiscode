#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json
import random
import urllib
import logging
import argparse
import coloredlogs

from pyquery import PyQuery

BASEDIR = os.path.dirname(os.path.abspath(__name__))
OUTPUTDIR = os.path.join(BASEDIR, 'output')

coloredlogs.install()


class Topic(object):

    """Topic class is used for representing Topic on Zhihu"""

    def __init__(self, name, id_):
        """Init topic object with name and id

        :name: name of topic
        :id_: id of topic

        """
        self._name = name
        self._id = id_

    def __unicode__(self):
        return '[topic: %s (%d)]' % (self.name, self.id)

    def __repr__(self):
        return unicode(self)

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def url(self):
        return 'http://www.zhihu.com/topic/%d/questions' % self._id

    @property
    def filepath(self):
        return os.path.join(OUTPUTDIR, '%d.json' % self.id)

    @property
    def finished(self):
        return os.path.exists(self.filepath)

    def url_for_page(self, page_number):
        if page_number <= 1: return self.url
        return self.url + '?' + urllib.urlencode({'page': page_number})

    def get_question(self, item):
        subtopicdom = item.children('.subtopic a')
        subtopic = subtopicdom.text().strip()
        subtopicid = int(subtopicdom.attr('href').split('/')[2])
        titledom = item.children('.question-item-title a')
        title = titledom.text().strip()
        questionid = int(titledom.attr('href').split('/')[2])

        logging.debug('question: %s(%d)' % (title, questionid))

        return {
            'id': questionid,
            'title': title,
            'subtopic': {
                'title': subtopic,
                'id': subtopicid,
            },
        }

    def get_questions(self, page):
        logging.info('processing: %s (page %d)' % (self, page))
        url = self.url_for_page(page)
        logging.debug('fetching: %s' % url)
        items = PyQuery(url)('.feed-item')
        return [self.get_question(PyQuery(item)) for item in items]

    def persist(self, count=200):
        if self.finished:
            logging.info("skipped %s" % self)
            return

        page = 1
        questions = []
        logging.info("start fetching %s" % self)
        while len(questions) < count and page < 100:
            try:
                questions.extend(self.get_questions(page))
                wait = random.randint(5, 60)
            except Exception, e:
                logging.error("failed to fetch and parse %s(page %d)" % (self, page))
                logging.exception(e)
                logging.debug("skipped %s(page %d)" % (self, page))
            finally:
                page += 1

                logging.debug('wait for %d seconds' % wait)
                time.sleep(wait)

        if len(questions) == 0:
            logging.error("failed to fetch or parse %s" % self)
            return

        obj = {
            'id': self.id,
            'name': self.name,
            'questions': questions,
        }

        logging.info('saving data for %s' % self)
        logging.debug('writing path: %s' % self.filepath)
        with open(self.filepath, 'w') as f:
            json.dump(obj, f)


def readtopics(path):
    topics = []
    with open(path) as f:
        for l in f.readlines():
            l = l.decode('utf8').strip()
            if not l: continue
            topicpair = l.split()
            topics.append((topicpair[0], int(topicpair[1])))
    return topics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="The file which contains the topics to be processed")
    args = parser.parse_args()
    if args.filename.strip():
        topics = readtopics(args.filename.strip())
        logging.info('%d topics to process' % len(topics))
        for tname, tid in topics:
            topic = Topic(tname, tid)
            topic.persist()
