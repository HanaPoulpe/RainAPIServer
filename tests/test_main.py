"""Test the main"""
import unittest

import stubber

import src.rain_server.main as main


class TestMain(unittest.TestCase):
    """
    Basic tests for full application.
    """
    def setUp(self) -> None:
        self.usage = stubber.CallableTracker("usage", main)
        self.version = stubber.CallableTracker("version", main)
        self.help = stubber.CallableTracker("help", main)

    def tearDown(self) -> None:
        self.usage.tear_down()
        self.help.tear_down()
        self.version.tear_down()

    def test_usage(self):
        """Test usage print"""
        main.main("--usage")

        self.assertEqual(len(self.version.calls), 1, "Usage should have been called.")

    def test_version(self):
        """Test version print"""
        main.main("--version")

        self.assertEqual(len(self.version.calls), 1, "Version should have been called.")

    def test_help(self):
        """Test help print"""
        main.main("--help")

        self.assertEqual(len(self.help.calls), 1, "Help should have been called.")


if __name__ == '__main__':
    unittest.main()
