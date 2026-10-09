"""API contract tests. No network or real token is used."""

import unittest
from unittest.mock import Mock, patch

import requests

import fpl_api


class APIContractTests(unittest.TestCase):
    def response(self, status=200, payload=None):
        response = Mock(status_code=status)
        response.json.return_value = payload if payload is not None else {"ok": True}
        return response

    @patch.object(fpl_api.session, "get")
    def test_public_request_has_timeout_and_no_token(self, get):
        get.return_value = self.response()
        with patch.object(fpl_api, "FPL_AUTH_TOKEN", "Bearer test-only"):
            self.assertEqual(fpl_api.get_bootstrap(), {"ok": True})
        args, kwargs = get.call_args
        self.assertTrue(args[0].endswith("/bootstrap-static/"))
        self.assertEqual(kwargs["headers"], {})
        self.assertEqual(kwargs["timeout"], (5, 20))
        self.assertFalse(kwargs["allow_redirects"])
        self.assertNotIn("X-API-Authorization", fpl_api.session.headers)

    @patch.object(fpl_api.session, "get")
    def test_current_squad_scopes_token_to_one_request(self, get):
        get.return_value = self.response(payload={"picks": []})
        with patch.object(fpl_api, "FPL_AUTH_TOKEN", "Bearer test-only"):
            self.assertEqual(fpl_api.get_my_team(123), {"picks": []})
        self.assertEqual(
            get.call_args.kwargs["headers"], {"X-API-Authorization": "Bearer test-only"}
        )
        self.assertTrue(get.call_args.args[0].endswith("/my-team/123/"))

    @patch.object(fpl_api.session, "get")
    def test_missing_token_does_not_make_request(self, get):
        with patch.object(fpl_api, "FPL_AUTH_TOKEN", None):
            with self.assertRaisesRegex(RuntimeError, "missing"):
                fpl_api.get_my_team(123)
        get.assert_not_called()

    @patch.object(fpl_api.session, "get")
    def test_invalid_json_is_an_actionable_error(self, get):
        get.return_value = self.response()
        get.return_value.json.side_effect = ValueError("private response")
        with self.assertRaisesRegex(RuntimeError, "invalid JSON"):
            fpl_api.get_bootstrap()

    @patch.object(fpl_api.session, "get")
    def test_scalar_payload_is_rejected(self, get):
        get.return_value = self.response(payload="unexpected")
        with self.assertRaisesRegex(RuntimeError, "response shape"):
            fpl_api.get_bootstrap()

    @patch.object(fpl_api.session, "get")
    def test_rate_limit_is_not_retried(self, get):
        get.return_value = self.response(status=429)
        with self.assertRaisesRegex(RuntimeError, "429"):
            fpl_api.get_bootstrap()
        self.assertEqual(get.call_count, 1)

    @patch.object(fpl_api.session, "get")
    def test_network_error_does_not_echo_private_details(self, get):
        get.side_effect = requests.ConnectionError("secret header")
        with self.assertRaises(RuntimeError) as error:
            fpl_api.get_bootstrap()
        self.assertNotIn("secret", str(error.exception))

    @patch.object(fpl_api.session, "get")
    def test_error_status_does_not_echo_response_body(self, get):
        get.return_value = self.response(status=500)
        get.return_value.text = "private response body"
        with self.assertRaises(RuntimeError) as error:
            fpl_api.get_bootstrap()
        self.assertIn("500", str(error.exception))
        self.assertNotIn("private", str(error.exception))

    @patch.object(fpl_api.session, "get")
    def test_redirect_is_not_followed(self, get):
        get.return_value = self.response(status=302)
        with self.assertRaisesRegex(RuntimeError, "302"):
            fpl_api.get_bootstrap()
        self.assertFalse(get.call_args.kwargs["allow_redirects"])


if __name__ == "__main__":
    unittest.main()
