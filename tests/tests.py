import unittest
from sed import Sed


class TestSed(unittest.TestCase):

    def tokenize(self, script):
        sed = Sed(script, quiet=True)
        return sed.tokens

    def runtest(self, script, string, expected):
        sed = Sed(script, quiet=True)
        sed.parseString(string)
        return sed._pattern_, expected

    def testTokenSubstitute(self):
        self.assertEqual(
            self.tokenize('s/a/b/'),
            ['s', '/', 'a', '/', 'b', '/']
        )

        self.assertEqual(
            self.tokenize('s/abc/123/'),
            ['s', '/', 'abc', '/', '123', '/']
        )

        self.assertEqual(
            self.tokenize('s_a_b_'),
            ['s', '_', 'a', '_', 'b', '_']
        )

        self.assertEqual(
            self.tokenize('1s/a/b/'),
            ['1', 's', '/', 'a', '/', 'b', '/']
        )

        self.assertEqual(
            self.tokenize('1~2s/a/b/'),
            ['1', '~2', 's', '/', 'a', '/', 'b', '/']
        )

        self.assertEqual(
            self.tokenize('1,5s/a/b/'),
            ['1', '5', 's', '/', 'a', '/', 'b', '/']
        )

        self.assertEqual(
            self.tokenize('1,$s/a/b/'),
            ['1', '$', 's', '/', 'a', '/', 'b', '/']
        )

        self.assertEqual(
            self.tokenize('/a/s/a/b/'),
            ['/', 'a', '/', 's', '/', 'a', '/', 'b', '/']
        )

        self.assertEqual(
            self.tokenize('/a/,/b/s/a/b/'),
            ['/', 'a', '/', '/', 'b', '/', 's', '/', 'a', '/', 'b', '/']
        )

    def testSubstitute(self):
        self.assertEqual(*self.runtest('s/a/b/',   'a',  'b'))
        self.assertEqual(*self.runtest('s/a/b/',   'aa', 'ba'))
        self.assertEqual(*self.runtest('s/a/b/g',  'aa', 'bb'))
        self.assertEqual(*self.runtest('s/a/b/i',  'A',  'b'))
        self.assertEqual(*self.runtest('s/a/b/ig', 'Aa', 'bb'))

    def testTranslate(self):
        self.assertEqual(*self.runtest('y/a/b/',     'aaa', 'bbb'))
        self.assertEqual(*self.runtest('y/abc/123/', 'abc', '123'))
