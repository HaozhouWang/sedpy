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

        self.hold = None
        self.pattern = None
        self.match = False

        self.sed = self.parser()
        self.commands = self.sed.parseString(self.script)

    def parser(self):
        """
        Sed Parser Generator
        """
        # Forward declaration of the pattern and replacemnt text as the delimter
        # can be any character and will we not know it's value until parse time
        # https://pythonhosted.org/pyparsing/pyparsing.Forward-class.html
        text = Forward()

        def define_text(script, position, token):
            """
            Closes round the scope of the text Forward and defines the
            pattern and replacement tokens after the delimter is known

            https://pythonhosted.org/pyparsing/pyparsing.ParserElement-class.html#setParseAction

            :param script: the script being parsed
            :param position: the position of the matched token
            :param token: the list of matched tokens
            """
            text << Word(printables + ' \t', excludeChars=token[0])

        flags = oneOf('g p i d').setName('flags')('flags')

        delimiter = Word(printables, exact=1).setName('delimiter')('delimiter')
        delimiter.setParseAction(define_text)

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
            Optional(text, '').setName('pattern')('pattern'),
            delimiter,
            Optional(text, '').setName('replacement')('replacement'),
            delimiter,
            ZeroOrMore(flags).setName('flags')('flags')
        ]).leaveWhitespace()('subsitution')

        subsitution.setParseAction(self.compileRegex)

        translate = reduce(operator.add, [
            Literal('y').setName('translate')('translate'),
            delimiter,
            text.setName('pattern')('pattern'),
            delimiter,
            text.setName('replacement')('replacement'),
            delimiter,
        ]).leaveWhitespace()('translateF')

        translate.setParseAction(self.translateF)

        actions = (subsitution | translate)
        return Optional(condition) + actions

    def parse_script(self, string):
        self.pattern = string
        for command in self.commands:
            command()

    def parse_file(self, fileh):
        for line in fileh:
            self.pattern = line
            for command in self.commands:
                if isfunction(command):
                    command()

    def check_condition(self, s, location, tokens):
        self.tokens.extend(tokens)

        def checker():
            self.match = True
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
            p = re.sub(regex, replace, self.pattern, count=g, flags=flags)
            self.pattern = p

            if not self.quiet:
                sys.stdout.write(self.pattern)

            if 'p' in s_flags:
                sys.stdout.write(self.pattern)

        return print_match

    def translateF(self, p, location, tokens):
        """
        tr
        """
        def tr():
            translatedLine = ''
            translate = zip(list(tokens.pattern), list(tokens.replacement))
            for char in self.pattern:
                for match, replace in translate:
                    if char == match:
                        translatedLine += replace
                        break
                else:
                    translatedLine += char

            self.pattern = translatedLine

            if not self.quiet:
                sys.stdout.write(translatedLine)

        return tr
