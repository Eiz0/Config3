import unittest
from config_parser import ConfigParser

class TestConfigParser(unittest.TestCase):
    def setUp(self):
        self.parser = ConfigParser()

    def test_constants(self):
        text = "set defaultAge = 25\nage = [defaultAge]"
        root = self.parser.parse(text)
        self.assertEqual(root[0].tag, "age")
        self.assertEqual(root[0].text, "25")

    def test_string(self):
        text = 'name = @"Иван Иванов"'
        root = self.parser.parse(text)
        self.assertEqual(root[0].tag, "name")
        self.assertEqual(root[0].text, "Иван Иванов")

    def test_number(self):
        text = "port = 8080"
        root = self.parser.parse(text)
        self.assertEqual(root[0].tag, "port")
        self.assertEqual(root[0].text, "8080")

    def test_array(self):
        text = 'hobbies = << @"чтение", @"путешествия" >>'
        root = self.parser.parse(text)
        self.assertEqual(root[0].tag, "hobbies")
        self.assertEqual(len(root[0]), 2)

    def test_struct(self):
        text = """
        user = struct {
            name = @"Иван",
            age = 30
        }
        """
        root = self.parser.parse(text)
        self.assertEqual(root[0].tag, "user")
        self.assertEqual(len(root[0]), 2)

if __name__ == "__main__":
    unittest.main()
