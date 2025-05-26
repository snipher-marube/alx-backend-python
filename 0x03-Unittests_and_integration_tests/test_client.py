import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock
from client import GithubOrgClient

class TestGithubOrgClient(unittest.TestCase):
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value"""
        # Set up the mock return value
        expected_response = {"login": org_name, "id": 1234}
        mock_get_json.return_value = expected_response

        # Create client instance and call the org method
        client = GithubOrgClient(org_name)
        result = client.org

        # Assert get_json was called once with correct URL
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

        # Assert we got the expected result
        self.assertEqual(result, expected_response)