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

        self.words = {}
        position = 1
        f = open(filename)

        for line in f:
            (word, freq) = line.split('\t')
            self.words[word] = position
            position = position + 1

        f.close()

        logging.info('dictionary init finished')
        
    def frequency(self, word):
        logging.info('query: %s' % word)
        try:
            return self.words[word]
        except Exception:
            return 0

    def word(self, frequency):
        for w, f in self.words.iteritems():
            if frequency == f:
                return w
        return ""


dictionary = Dictionary('data/frequency_list.txt')

class MainHandler(webapp.RequestHandler):

    def get(self):

        values = {}

        word = self.request.get('word')
        if word == "":
            #null request
            pass
        elif word.isdigit():
            #request word in certain position
            frequency = int(word)
            values["position"] = word

            found_word = dictionary.word(frequency)
            if found_word:
                #dictionary is less then required position
                values["word_in_position"] = found_word
        
        else:
            #simple word request
            values["word"] = word
            frequency = dictionary.frequency(word)
            if frequency > 0:
                values["frequency"] = frequency


        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'form.html')
        self.response.out.write(template.render(path, values, DEBUG))


def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
