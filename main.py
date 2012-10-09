#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

import logging
import os


DEBUG = True


class Dictionary:
    def __init__(self, filename):
        logging.info('dictionary init started')

        self.words = []
        with open(filename) as fin:
            for line in fin:
                word, freq = line.strip().split('\t')
                self.words.append(word)

        logging.info('dictionary init finished')

    def order(self, word):
        if word not in self.words:
            return None
        return self.words.index(word) + 1

    def word(self, order):
        index = order - 1
        if index < 0 or index >= len(self.words):
            return None
        return self.words[index]

    def suggest(self, begin):
        suggest_len = 5
        return filter(lambda w: w.startswith(begin), self.words)[:suggest_len]
        
dictionary = Dictionary('data/frequency_list.txt')


class WordHandler(webapp.RequestHandler):
    def get(self):
        order = int(self.request.get('order'))
        word = dictionary.word(order)
        if word is None:
            self.response.out.write('[]')
            return
        self.response.out.write('["{0}"]'.format(word))


class OrderHandler(webapp.RequestHandler):
    def get(self):
        word = self.request.get('word')
        order = dictionary.order(word)
        if order is None:
            self.response.out.write('[]')
            return
        self.response.out.write('[{0}]'.format(order))


class SuggestHandler(webapp.RequestHandler):
    def get(self):
        begin = self.request.get('begin')
        suggest = dictionary.suggest(begin)
        json = '[' + ', '.join(['"{0}"'.format(s) for s in suggest]) + ']'
        self.response.out.write(json)


def main():
    handlers = [
        ('/word', WordHandler),
        ('/order', OrderHandler),
        ('/suggest', SuggestHandler)
        ]
    application = webapp.WSGIApplication(handlers, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
