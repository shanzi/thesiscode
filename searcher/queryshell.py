#!/usr/bin/env python
# -*- coding: utf-8 -*-


import cmd
import argparse

from queryhandler import (
    BoolQueryHandler,
    ConceptualGraphQueryHandler,
)


class QueryShell(cmd.Cmd):

    """Interactive shell for query"""

    intro = """
An interactive shell for testing query functions.
    """

    def __init__(self, indexpath, *args, **kwargs):
        cmd.Cmd.__init__(self, *args, **kwargs)

        self._indexpath = indexpath
        self._handler = None
        self._handlerdict = {}

    @property
    def prompt(self):
        if isinstance(self._handler, BoolQueryHandler):
            return '(bool): '
        elif isinstance(self._handler, ConceptualGraphQueryHandler):
            return '(concept): '
        else:
            return '(no handler): '

    def output_result(self, res):
        for i, r in enumerate(res, 1):
            question, _, score = r
            print u'%2d. %s [%.2f]' % (i, question['title'], score)

    def do_handler(self, handler):
        "Switch between `bool` handler and `cg` handler"
        hdict = self._handlerdict
        if handler == 'bool':
            hdict['bool'] = hdict.get('bool') or BoolQueryHandler(self._indexpath)
        elif handler == 'cg':
            hdict['cg'] = hdict.get('cg') or ConceptualGraphQueryHandler(self._indexpath)
        else:
            print '*** Unknown handler: ', handler
        self._handler = hdict.get(handler)

    def do_query(self, query):
        "Perform query with selected handler"
        if self._handler:
            query = query.decode('utf8')
            res = self._handler.query(filter(None, query.split()))
            self.output_result(res)
        else:
            print '*** No handler is selected.'

    def do_exit(self, line):
        "Exit the shell"
        return True

    def do_EOF(self, line):
        "Exit the shell."
        print 'Exit.'
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='Path to index file')
    args = parser.parse_args()
    if args.path:
        shell = QueryShell(args.path)
        shell.cmdloop()
