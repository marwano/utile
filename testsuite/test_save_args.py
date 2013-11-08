
from testsuite.support import TestCase
from utile import save_args


class Fruit(object):
    @save_args
    def __init__(self, name=None, color=None):
        pass


class SaveArgsTestCase(TestCase):
    def test_positional_args(self):
        apple = Fruit('apple', 'red')
        self.assertEqual(apple.name, 'apple')
        self.assertEqual(apple.color, 'red')

    def test_keyword_args(self):
        apple = Fruit(color='red', name='apple')
        self.assertEqual(apple.name, 'apple')
        self.assertEqual(apple.color, 'red')

    def test_default_args(self):
        red_fruit = Fruit(color='red')
        self.assertEqual(red_fruit.name, None)
        self.assertEqual(red_fruit.color, 'red')
