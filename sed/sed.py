import re
import sys
import operator
from inspect import isfunction
from pyparsing import printables, oneOf, nums
from pyparsing import Literal, Word, Forward, Regex
from pyparsing import Optional, ZeroOrMore, Suppress


class Sed(object):
    """
    SED implemented in Python using pyarsing
    """
    def __init__(self, script, quiet=False):

        self.script = script
        self.quiet = quiet

        self.tokens = []

        self._hold_ = None
        self._pattern_ = None
        self._match_ = False

        self.FLAGS = oneOf('g p i d').setName('flags')('flags')

        self.text = Forward()

        delimiter = Word(printables, exact=1).setName('delimiter')('delimiter')
        delimiter.setParseAction(self.excludingDelimiter)

        step = Regex('~[0-9]+')
        step.setName('step')('step')

        num_address = Word(nums + '$') + Optional(step)
        num_address.setName('num_address')('num_address')

        regex_address = reduce(operator.add, [
            Literal('/'),
            Word(printables, excludeChars='/'),
            Literal('/'),
            Optional(Literal('i'))
        ])

        regex_address.setName('regex-address')('regex-address')

        address = (num_address | regex_address).setName('address')('address')
        condition = address + Optional(Suppress(Literal(',')) + address)
        condition.setName('condition')('condition')

        condition.setParseAction(self.check_condition)

        subsitution = reduce(operator.add, [
            Literal('s').setName('sflag')('sflag'),
            delimiter,
            Optional(self.text, '').setName('pattern')('pattern'),
            delimiter,
            Optional(self.text, '').setName('replacement')('replacement'),
            delimiter,
            ZeroOrMore(self.FLAGS).setName('flags')('flags')
        ]).leaveWhitespace()('subsitution')

        subsitution.setParseAction(self.compileRegex)

        translate = reduce(operator.add, [
            Literal('y').setName('translate')('translate'),
            delimiter,
            self.text.setName('pattern')('pattern'),
            delimiter,
            self.text.setName('replacement')('replacement'),
            delimiter,
        ]).leaveWhitespace()('translateF')

        translate.setParseAction(self.translateF)

        actions = (subsitution | translate)
        self.sed = Optional(condition) + actions
        self.commands = self.sed.parseString(self.script)

    def parseFile(self, fileh):
        for line in fileh:
            self._pattern_ = line
            for command in self.commands:
                if isfunction(command):
                    command()

    def parseString(self, string):
        self._pattern_ = string
        for command in self.commands:
            command()

    def excludingDelimiter(self, s, l, t):
        """
        Exclude the delimiter from the pattern and replacement
        """
        self.text << Word(printables + ' \t', excludeChars=t[0])

    def check_condition(self, s, location, tokens):
        self.tokens.extend(tokens)

        def checker():
            self._match_ = True
        return checker

    def compileRegex(self, p, location, tokens):
        """
        Return subsitution function
        """
        self.tokens.extend(tokens)

        def print_match():

            s_flags = list(tokens.flags)
            g = int('g' not in s_flags)
            flags = re.IGNORECASE if 'i' in s_flags else 0

            regex = tokens.pattern
            replace = tokens.replacement
            p = re.sub(regex, replace, self._pattern_, count=g, flags=flags)
            self._pattern_ = p

            if not self.quiet:
                sys.stdout.write(self._pattern_)

            if 'p' in s_flags:
                sys.stdout.write(self._pattern_)

        return print_match

    def translateF(self, p, location, tokens):
        """
        tr
        """
        def tr():
            translatedLine = ''
            translate = zip(list(tokens.pattern), list(tokens.replacement))
            for char in self._pattern_:
                for match, replace in translate:
                    if char == match:
                        translatedLine += replace
                        break
                else:
                    translatedLine += char

            self._pattern_ = translatedLine

            if not self.quiet:
                sys.stdout.write(translatedLine)

        return tr
