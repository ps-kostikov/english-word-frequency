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


def load_dictionary(filename):
    words = []
    with open(filename) as fin:
        for line in fin:
            word, freq = line.strip().split('\t')
            words.append(word)
    return words


dictionary = load_dictionary('data/frequency_list.txt')


class Language:
    def __init__(self, langtag):
        self._langtag = langtag

    def filename(self):
        return 'translations/{0}.ini'.format(self._langtag)

    def translations(self):
        result = {}
        with open(self.filename()) as fin:
            for line in fin:
                key, value = line.strip().split('=')
                result[key] = value
        return result

    def translate(self, html):
        return html.format(**self.translations())


def get_language(request):
    default_langtag = 'en'
    langtag = default_langtag
    if 'Accept-Language' in request.headers:
        if request.headers['Accept-Language'].lower().startswith('ru'):
            langtag = 'ru'

    return Language(langtag)


class WordHandler(webapp.RequestHandler):
    def get(self):
        order = int(self.request.get('order'))

        index = order - 1
        if index < 0 or index >= len(dictionary):
            self.response.set_status(404)
            return

        word = dictionary[index]
        json = '["{0}"]'.format(word)
        self.response.out.write(json)


class OrderHandler(webapp.RequestHandler):
    def get(self):
        word = self.request.get('word')

        if word not in dictionary:
            self.response.set_status(404)
            return

        order = dictionary.index(word) + 1
        json = '["{0}"]'.format(order)
        self.response.out.write(json)


class SuggestHandler(webapp.RequestHandler):
    def get(self):
        begin = self.request.get('begin')

        suggest_len = 5
        words = filter(lambda w: w.startswith(begin), dictionary)[:suggest_len]

        json = '[' + ', '.join(['"{0}"'.format(w) for w in words]) + ']'
        self.response.out.write(json)


class MainHandler(webapp.RequestHandler):
    def get(self):
        language = get_language(self.request)
        with open('form.html') as out:
            html = out.read()
        translation = language.translate(html)
        self.response.out.write(translation)


class IntervalHandler(webapp.RequestHandler):
    def get(self):
        word = self.request.get('word')

        if word.isdigit():
            self.handle_order(int(word))
        else:
            self.handle_word(word)

    def response_by_index(self, index):
        shift = 2
        output_size = 5

        l = len(dictionary)
        if index - shift < 0:
            begin, end = 0, output_size
        elif index + shift >= l:
            begin, end = l - output_size, l
        else:
            begin, end = index - shift, index - shift + output_size

        parts = []
        for i in range(output_size):
            parts.append('["{word}", "{order}"]'.format(
                    word = dictionary[begin + i],
                    order = begin + i + 1
                    ))

        json = '[' + ', '.join(parts) + ']'
        self.response.out.write(json)

    def handle_order(self, order):
        index = order - 1
        if index < 0 or index >= len(dictionary):
            self.response.set_status(404)
            return
        self.response_by_index(index)

    def handle_word(self, word):
        if word not in dictionary:
            self.response.set_status(404)
            return
        self.response_by_index(dictionary.index(word))


def main():
    handlers = [
        ('/', MainHandler),
        ('/index.html', MainHandler),
        ('/word', WordHandler),
        ('/order', OrderHandler),
        ('/suggest', SuggestHandler),
        ('/interval', IntervalHandler)
        ]
    application = webapp.WSGIApplication(handlers, debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
