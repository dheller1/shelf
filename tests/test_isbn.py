import pytest

from shelf.core.isbn import ISBN

class TestISBN:
    def test_ctor(self):
        s = 'ISBN 978-1-80107-931-0'
        _ = ISBN(s)

        with pytest.raises(SyntaxError):
            ISBN('foo')

    def test_find(self):
        test_str = ("foo\n"
                    "bar\n"
                    "bazbazbaz\n"
                    "quuuuuuuuuuuuuuuxx ISBN 978-1-80107-931-0\n"
                    "lorem ipsum")

        f = ISBN.find(test_str)
        assert f
        assert isinstance(f, ISBN)
        assert str(f) == 'ISBN: 978-1-80107-931-0'
        assert ISBN.find('lsdhalfdhaslasdhlkashlkaslkhgdhlasdhk') is None
        f2 = ISBN.find(str(f))
        assert str(f2) == str(f)

    def test_digits(self):
        i = ISBN('ISBN 978-1-80107-931-0')
        assert i.digits() == '9781801079310'
