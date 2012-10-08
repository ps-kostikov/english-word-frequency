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

        # self.words = {}
        # position = 1
        # f = open(filename)

        # for line in f:
        #     (word, freq) = line.split('\t')
        #     self.words[word] = position
        #     position = position + 1

        # f.close()

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
        
    # def frequency(self, word):
    #     logging.info('query: %s' % word)
    #     try:
    #         return self.words[word]
    #     except Exception:
    #         return 0

    # def word(self, frequency):
    #     for w, f in self.words.iteritems():
    #         if frequency == f:
    #             return w
    #     return ""


dictionary = Dictionary('data/frequency_list.txt')

class WordHandler(webapp.RequestHandler):
    def get(self):
        order = int(self.request.get('order'))
        word = dictionary.word(order)
        if word is None:
            word = 'blah'
            # self.response.out.write('{}')
            # return
        self.response.out.write('["{0}"]'.format(word))


class OrderHandler(webapp.RequestHandler):
    def get(self):
        word = self.request.get('word')
        order = dictionary.order(word)
        if order is None:
            order = 1000
            # self.response.out.write('{}')
            # return
        self.response.out.write('[{0}]'.format(order))


class SuggestHandler(webapp.RequestHandler):
    def get(self):
        begin = self.request.get('begin')
        suggest = dictionary.suggest(begin)
        json = '[' + ', '.join(['"{0}"'.format(s) for s in suggest]) + ']'
        self.response.out.write(json)


class MainHandler(webapp.RequestHandler):
    def get(self):
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'form.html')
        self.response.out.write(template.render(path, {}, DEBUG))


# class MainHandler(webapp.RequestHandler):

#     def get(self):

#         values = {}

#         word = self.request.get('word')
#         if word == "":
#             #null request
#             pass
#         elif word.isdigit():
#             #request word in certain position
#             frequency = int(word)
#             values["position"] = word

#             found_word = dictionary.word(frequency)
#             if found_word:
#                 #dictionary is less then required position
#                 values["word_in_position"] = found_word
        
#         else:
#             #simple word request
#             values["word"] = word
#             frequency = dictionary.frequency(word)
#             if frequency > 0:
#                 values["frequency"] = frequency


#         directory = os.path.dirname(__file__)
#         path = os.path.join(directory, 'form.html')
#         self.response.out.write(template.render(path, values, DEBUG))


def main():
    handlers = [
        ('/', MainHandler),
        ('/word', WordHandler),
        ('/order', OrderHandler),
        ('/suggest', SuggestHandler)
        ]
    application = webapp.WSGIApplication(handlers, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
