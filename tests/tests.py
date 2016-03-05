from sed import Sed
from unittest import TestCase


class SedTestRunner(object):
    """
    Utility functions for use with the test suite
    """
    def tokenize(self, script):
        """
        Return the token array for a given script
        """
        sed = Sed(script, quiet=True)
        return sed.tokens

    def runtest(self, script, string, expected):
        """
        Run a script on a string, returns the output and expected
        """
        sed = Sed(script, quiet=True)
        sed.parseString(string)
        return sed._pattern_, expected


class TestTokenization(TestCase, SedTestRunner):

    def testSimpleSubstitution1(self):
        """
        TOKEN1: single character pattern and replacement substitution
        """
        self.assertEqual(
            self.tokenize('s/a/b/'),
            ['s', '/', 'a', '/', 'b', '/']
        )

    def testSimpleSubstitution2(self):
        """
        TOKEN2: multi character pattern and replacement substitution
        """
        self.assertEqual(
            self.tokenize('s/abc/123/'),
            ['s', '/', 'abc', '/', '123', '/']
        )

    def testSimpleSubstitution3(self):
        """
        TOKEN3: substitution with non standard delimiter
        """
        self.assertEqual(
            self.tokenize('s_a_b_'),
            ['s', '_', 'a', '_', 'b', '_']
        )

    def testSimpleSubstitution4(self):
        """
        TOKEN4: substitution with numeric address
        """
        self.assertEqual(
            self.tokenize('1s/a/b/'),
            ['1', 's', '/', 'a', '/', 'b', '/']
        )

    def testSimpleSubstitution5(self):
        """
        TOKEN5: substitution with numeric address + offset
        """
        self.assertEqual(
            self.tokenize('1~2s/a/b/'),
            ['1', '~2', 's', '/', 'a', '/', 'b', '/']
        )

    def testSimpleSubstitution6(self):
        """
        TOKEN6: substitution with numeric address range
        """
        self.assertEqual(
            self.tokenize('1,5s/a/b/'),
            ['1', '5', 's', '/', 'a', '/', 'b', '/']
        )

    def testSimpleSubstitution7(self):
        """
        TOKEN7: substitution with end of file address
        """
        self.assertEqual(
            self.tokenize('1,$s/a/b/'),
            ['1', '$', 's', '/', 'a', '/', 'b', '/']
        )

    def testSimpleSubstitution8(self):
        """
        TOKEN8: substitution with regex address
        """
        self.assertEqual(
            self.tokenize('/a/s/a/b/'),
            ['/', 'a', '/', 's', '/', 'a', '/', 'b', '/']
        )

    def testSimpleSubstitution9(self):
        """
        TOKEN9: substitution with regex address range
        """
        self.assertEqual(
            self.tokenize('/a/,/b/s/a/b/'),
            ['/', 'a', '/', '/', 'b', '/', 's', '/', 'a', '/', 'b', '/']
        )


class TestSubstitution(TestCase, SedTestRunner):

    def testSubstitute(self):
        """
        SUB1: single character substitution, single character input
        """
        self.assertEqual(*self.runtest('s/a/b/',   'a',  'b'))

    def testSubstitute2(self):
        """
        SUB2: single character substitution, multiple character input
        """
        self.assertEqual(*self.runtest('s/a/b/',   'aa', 'ba'))
        self.assertEqual(*self.runtest('s/a/b/',   'aa', 'ba'))

    def testSubstitute3(self):
        """
        SUB3: single character global substitution, multiple character input
        """
        self.assertEqual(*self.runtest('s/a/b/g',  'aa', 'bb'))

    def testSubstitute4(self):
        """
        SUB4: single character case insensitive substitution
        """
        self.assertEqual(*self.runtest('s/a/b/i',  'A',  'b'))

    def testSubstitute5(self):
        """
        SUB5: single character case insensitive global substitution
        """
        self.assertEqual(*self.runtest('s/a/b/ig', 'Aa', 'bb'))


class TestTranslation(TestCase, SedTestRunner):

    def testTranslate(self):
        """
        TR1: single character translation
        """
        self.assertEqual(*self.runtest('y/a/b/',     'aaa', 'bbb'))

    def testTranslate2(self):
        """
        TR2: multi character translation
        """
        self.assertEqual(*self.runtest('y/abc/123/', 'abc', '123'))
        self.assertEqual(*self.runtest('y/abc/123/', 'a2c', '123'))
