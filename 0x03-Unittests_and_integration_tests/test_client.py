#!/usr/bin/env python3
import unittest
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from unittest.mock import patch, PropertyMock, Mock
from fixtures import TEST_PAYLOADS

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


class TestGithubOrgClient(unittest.TestCase):
    def test_public_repos_url(self):
        """Test that _public_repos_url returns the correct URL from org payload"""
        # Test payload with known repos_url
        test_payload = {
            "repos_url": "https://api.github.com/orgs/testorg/repos"
        }

        # Patch the org property to return our test payload
        with patch.object(
            GithubOrgClient, 
            'org', 
            new_callable=PropertyMock, 
            return_value=test_payload
        ) as mock_org:
            # Create client instance
            client = GithubOrgClient('testorg')
            
            # Get the _public_repos_url
            result = client._public_repos_url
            
            # Verify org property was accessed
            mock_org.assert_called_once()
            
            # Verify correct URL was returned
            self.assertEqual(result, test_payload['repos_url'])

class TestGithubOrgClient(unittest.TestCase):
    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns the correct list of repos"""
        # Test data
        test_repos_url = "https://api.github.com/orgs/testorg/repos"
        test_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
        ]
        expected_repos = ["repo1", "repo2"]

        # Configure mock return values
        mock_get_json.return_value = test_repos_payload

        # Patch _public_repos_url property
        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock,
            return_value=test_repos_url
        ) as mock_public_repos_url:
            # Create client instance
            client = GithubOrgClient('testorg')
            
            # Call the method
            repos = client.public_repos()
            
            # Assert the results
            self.assertEqual(repos, expected_repos)
            
            # Assert mocks were called correctly
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(test_repos_url)
        
class TestGithubOrgClient(unittest.TestCase):
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected_result):
        """Test that has_license correctly identifies license matches"""
        # Create client instance (org name doesn't matter for this test)
        client = GithubOrgClient('testorg')
        
        # Call the method and assert the result
        result = client.has_license(repo, license_key)
        self.assertEqual(result, expected_result)

@parameterized_class(('org_payload', 'repos_payload', 'expected_repos', 'apache2_repos'), 
                   TEST_PAYLOADS)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test for GithubOrgClient.public_repos"""
    
    @classmethod
    def setUpClass(cls):
        """Set up class fixtures before running tests"""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()
        
        # Configure side effect to return different payloads based on URL
        def side_effect(url):
            mock_response = Mock()
            if "orgs/" in url:
                mock_response.json.return_value = cls.org_payload
            elif "repos" in url:
                mock_response.json.return_value = cls.repos_payload
            return mock_response
            
        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop the patcher after all tests"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected repos"""
        client = GithubOrgClient('testorg')
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos with license filter"""
        client = GithubOrgClient('testorg')
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)

@parameterized_class(('org_payload', 'repos_payload', 'expected_repos', 'apache2_repos'), 
                   TEST_PAYLOADS)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test for GithubOrgClient.public_repos"""
    
    @classmethod
    def setUpClass(cls):
        """Set up class fixtures before running tests"""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()
        
        # Configure side effect to return different payloads based on URL
        def side_effect(url):
            mock_response = Mock()
            if "orgs/" in url:
                mock_response.json.return_value = cls.org_payload
            elif "repos" in url:
                mock_response.json.return_value = cls.repos_payload
            return mock_response
            
        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop the patcher after all tests"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns expected repos"""
        client = GithubOrgClient('testorg')
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)
        
        # Verify the mock was called with the correct URLs
        org_url = f"https://api.github.com/orgs/testorg"
        repos_url = self.org_payload['repos_url']
        self.mock_get.assert_any_call(org_url)
        self.mock_get.assert_any_call(repos_url)

    def test_public_repos_with_license(self):
        """Test public_repos with license filter"""
        client = GithubOrgClient('testorg')
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)
        
        # Verify the mock was called with the correct URLs
        org_url = f"https://api.github.com/orgs/testorg"
        repos_url = self.org_payload['repos_url']
        self.mock_get.assert_any_call(org_url)
        self.mock_get.assert_any_call(repos_url)
