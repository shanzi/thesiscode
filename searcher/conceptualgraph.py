#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import weakref
from StringIO import StringIO


CONCEPT = re.compile(ur"\[(?P<cid>\w+)(?P<root>\*)? (?P<entity>.+?)]")
RELATION = re.compile(ur"\((?P<rtype>.+?) (?P<cid1>\w+) (?P<cid2>\w+)\)")


class ConceptNode(object):
    def __init__(self, entity):
        self._entity = entity
        self.out_relations = set()

    def __unicode__(self):
        return u'[%s]' % self._entity

    def __repr__(self):
        return unicode(self)

    def output(self, tab=0):
        print unicode(self),
        ntab = tab + len(self._entity) * 2 + 2
        for i, rel in enumerate(self.out_relations):
            if i > 0: print '\n', ' ' * ntab,
            print '->',
            rel.output(ntab + 4)


class RelationNode(object):
    def __init__(self, name, prev, next):
        self._name = name
        self._prev_ref = weakref.ref(prev)
        self._next_ref = next

    def __unicode__(self):
        return u'(%s)' % self._name

    def __repr__(self):
        return unicode(self)

    @property
    def prev(self):
        return self._prev_ref()  # self._prev_ref is a weakref object

    @property
    def next(self):
        return self._next_ref

    def output(self, tab=0):
        print unicode(self), '->',
        ntab = tab + len(self._name) * 2 + 6
        self.next.output(ntab)


class ConceptualGraph(object):

    """Python representation of a Conceptual Graph"""

    def __init__(self, root):
        self._root = root

    def __unicode__(self):
        return u'(CGIF: %s)' % self._root

    def __repr__(self):
        return unicode(self)

    def output(self):
        self._root.output()

    @classmethod
    def loads(cls, string):
        conceptnodes = {}
        root = None
        for m in CONCEPT.finditer(string):
            mdict = m.groupdict()
            node = ConceptNode(mdict['entity'])
            conceptnodes[mdict['cid']] = node
            if mdict['root']: root = node
        for m in RELATION.finditer(string):
            mdict = m.groupdict()
            rtype = mdict['rtype']
            cid1 = mdict['cid1']
            cid2 = mdict['cid2']
            c1 = conceptnodes[cid1]
            c2 = conceptnodes[cid2]
            rel = RelationNode(rtype, c1, c2)
            c1.out_relations.add(rel)
        return cls(root)

    @classmethod
    def load(cls, fp):
        return cls.loads(fp.read().decode('utf8'))


if __name__ == "__main__":
    with open('test.cgif') as f:
        g = ConceptualGraph.load(f)
        g.output()
