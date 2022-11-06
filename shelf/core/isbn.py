import re

# https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch04s13.html
# (Variations: Find ISBNs in documents) -- the MULTILINE is important !!!
_isbn_in_doc = re.compile(r"\bISBN(?:-1[03])?:? (?=[0-9X]{10}$|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[- ]){4})[- 0-9]{17}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]\b", re.MULTILINE)
_isbn_plain = re.compile(r"^(?:ISBN(?:-1[03])?:? )?(?=[0-9X]{10}$|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[- ]){4})[- 0-9]{17}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]$")

class ISBN:
    def __init__(self, string):
        if not _isbn_plain.match(string):
            raise SyntaxError('invalid ISBN format')

        # Remove ISBN prefix and trim spaces
        self._isbn = re.sub('^ISBN(?:-1[03])?:?', '', string).strip()

    def __str__(self):
        return f'ISBN: {self._isbn}'

    @staticmethod
    def find(s):
        """ Finds the first ISBN in a long string `s`. """
        match = _isbn_in_doc.search(s)
        if match:
            assert _isbn_plain.match(match.group())
            return ISBN(match.group())
        return None

    def digits(self):
        """ Returns the ISBN in a digit-only representation (a string of 10 or 13 digits). """
        return re.sub('[ -]', '', self._isbn)


if __name__ == '__main__':
    test_str = ("foo\n"
                "bar\n"
                "bazbazbaz\n"
                "quuuuuuuuuuuuuuuxx ISBN 978-1-80107-931-0\n"
                "lorem ipsum")

    test = ISBN.find(test_str)
    print(test)
    print(test.digits())