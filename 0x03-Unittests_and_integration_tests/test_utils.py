#!/usr/bin/env python3
import unittest
from parameterized import parameterized
from utils import access_nested_map
from unittest.mock import patch, Mock
from utils import get_json
from utils import memoize
from client import GithubOrgClient


class TestAccessNestedMap(unittest.TestCase):
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test that access_nested_map returns the expected result"""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "'a'"),
        ({"a": 1}, ("a", "b"), "'b'"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_msg):
        """Test that access_nested_map raises KeyError with expected message"""
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), expected_msg)

    class TestGetJson(unittest.TestCase):
        @parameterized.expand([
            ("http://example.com", {"payload": True}),
            ("http://holberton.io", {"payload": False}),
        ])
        def test_get_json(self, test_url, test_payload):
            """Test that get_json returns the expected result with mocked requests.get"""
            # Create a mock response object
            mock_response = Mock()
            mock_response.json.return_value = test_payload
    
            # Patch requests.get to return our mock response
            with patch('requests.get', return_value=mock_response) as mock_get:
                # Call the function
                result = get_json(test_url)
    
                # Assert the mock was called correctly
                mock_get.assert_called_once_with(test_url)
    
                # Assert we got the expected result
                self.assertEqual(result, test_payload)

class TestMemoize(unittest.TestCase):
    def test_memoize(self):
        """Test that the memoize decorator caches the result"""
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        # Create instance of test class
        test_instance = TestClass()

        # Patch a_method to track calls and return 42
        with patch.object(TestClass, 'a_method', return_value=42) as mock_method:
            # First call - should call a_method
            result1 = test_instance.a_property
            # Second call - should use cached result
            result2 = test_instance.a_property

            # Assert correct results
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            
            # Assert a_method was only called once
            mock_method.assert_called_once()
