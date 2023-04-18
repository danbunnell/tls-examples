import json
import unittest
import warnings

import dns.resolver
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import SSLError
from urllib3.exceptions import InsecureRequestWarning
from urllib3.util.ssl_match_hostname import CertificateError

from src.adapters import AlternateHostnameAdapter

TEST_HOST = "example.org"
HOSTNAME_MISMATCH_REGEX_PATTERN = r"hostname '[\w\.]+' doesn't match"
UNVERIFIED_REQUEST_REGEX_PATTERN = r"Unverified HTTPS request is being made to host '[\w\.]+'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings"
_RESOLVER = dns.resolver.Resolver()

def _to_https(hostname):
    return f"https://{hostname}"

def _get_addresses(domain):
    records = _RESOLVER.resolve(domain, "A")

    addresses = []
    for record in records:
        addresses.append(record.to_text())

    # ex. addresses=['157.240.254.12']
    return addresses

def _get_ip_addr(domain):
    addresses = _get_addresses(domain)

    return addresses[0]


def _print_response(response):
    print(f"Status Code: {response.status_code}")
    print(f"Headers Length (Count): {len(response.headers)}")
    #print(f"Headers: {response.headers}")
    print(f"Encoding: {response.encoding}")
    #print(f"Text: {response.text}")
    print(f"Text Length (Bytes): {len(response.text)}")
    #print(f"JSON: {response.json()}")

class TestRequests(unittest.TestCase):
    """Tests the request module for behavior"""
    def test_default_when_hostname_match(self):
        uri = _to_https(TEST_HOST)

        response = requests.get(uri)

        self.assertTrue(200, response.status_code)

    def test_default_when_hostname_mismatch(self):
        ip_addr = _get_ip_addr(TEST_HOST)
        uri = _to_https(ip_addr)

        with self.assertRaises(SSLError) as ctx:
            response = requests.get(uri)

        self.assertRegex(ctx.exception.__str__(), HOSTNAME_MISMATCH_REGEX_PATTERN)

    def test_verify_when_hostname_match(self):
        uri = _to_https(TEST_HOST)

        response = requests.get(uri, verify=True)

        self.assertTrue(200, response.status_code)

    def test_verify_when_hostname_mismatch(self):
        ip_addr = _get_ip_addr(TEST_HOST)
        uri = _to_https(ip_addr)

        with self.assertRaises(SSLError) as ctx:
            response = requests.get(uri, verify=True)

        self.assertRegex(ctx.exception.__str__(), HOSTNAME_MISMATCH_REGEX_PATTERN)

    def test_no_verify_when_hostname_match(self):
        uri = _to_https(TEST_HOST)

        with warnings.catch_warnings(record=True) as warning_ctx:
            response = requests.get(uri, verify=False)

        self.assertTrue(200, response.status_code)
        self.assertEqual(warning_ctx[0].category, InsecureRequestWarning)
        self.assertRegex(str(warning_ctx[0].message), UNVERIFIED_REQUEST_REGEX_PATTERN)

    def test_no_verify_when_hostname_mismatch(self):
        ip_addr = _get_ip_addr(TEST_HOST)
        uri = _to_https(ip_addr)

        with warnings.catch_warnings(record=True) as warning_ctx:
            response = requests.get(uri, verify=False)

        self.assertTrue(200, response.status_code)
        self.assertEqual(warning_ctx[0].category, InsecureRequestWarning)
        self.assertRegex(str(warning_ctx[0].message), UNVERIFIED_REQUEST_REGEX_PATTERN)

    def test_verify_pass_when_cert_match_alt_host(self):
        ip_addr = _get_ip_addr(TEST_HOST)
        ip_uri = _to_https(ip_addr)
        domain_uri = _to_https(TEST_HOST)

        with requests.Session() as session:
            session.mount(ip_uri, AlternateHostnameAdapter(TEST_HOST))
            response = session.get(ip_uri)

        self.assertTrue(200, response.status_code)

    def test_verify_fail_when_cert_mismatch_alt_host(self):
        ip_addr = _get_ip_addr(TEST_HOST)
        ip_uri = _to_https(ip_addr)
        domain_uri = _to_https(TEST_HOST)

        with requests.Session() as session:
            session.mount(ip_uri, AlternateHostnameAdapter("notamatch.com"))

            with self.assertRaises(SSLError) as ctx:
                response = session.get(ip_uri)

            self.assertRegex(ctx.exception.__str__(), HOSTNAME_MISMATCH_REGEX_PATTERN)
