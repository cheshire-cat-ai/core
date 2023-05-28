from unittest import TestCase
from cat.utils import to_camel_case


class TestUtils(TestCase):
    """Tests utils functions."""

    def test_to_camel_case(self):
        self.assertEqual(
            "SomeText",
            to_camel_case("some text")
        )
        self.assertEqual(
            "SomeText",
            to_camel_case("some-text")
        )
        self.assertEqual(
            "SomeText",
            to_camel_case("some_text")
        )
