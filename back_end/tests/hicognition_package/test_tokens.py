"""Tests the tokens of app.lib.tokens against tokens itsdangerous 1.1 wrote.

The two tokens were made in the image the lab's instance ran at v0.8.0, with the secret key
SECRET: a session token with JSONWebSignatureSerializer, and a login token valid for a day with
TimedJSONWebSignatureSerializer, issued at ISSUED.
"""

import unittest

from app.lib import tokens

SECRET = "reference-secret"
ISSUED = 1700000000
SESSION_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzZXNzaW9uX2lkIjo3fQ.gcFI0it4uCTuOdZeuBYJb_nFo4pEZkqwJLqCgrDqSBmWs5Y2S-7VsDC0s-GLZFW_4LYVimp9tGf4qven6CnGvQ"
LOGIN_TOKEN = "eyJhbGciOiJIUzUxMiIsImlhdCI6MTcwMDAwMDAwMCwiZXhwIjoxNzAwMDg2NDAwfQ.eyJpZCI6M30.zHi7KDaqhSEiYP40EXW-nhRTjrQPQHY3U8dd3eHkZJna0-W1yICPN_3dWRJDpVGaF0ePjNcHQYo4hGlC1Yhzqw"


class TestTokens(unittest.TestCase):
    def test_writes_the_tokens_itsdangerous_wrote(self):
        self.assertEqual(tokens.dumps({"session_id": 7}, SECRET), SESSION_TOKEN)
        self.assertEqual(
            tokens.dumps({"id": 3}, SECRET, expires_in=86400, now=ISSUED), LOGIN_TOKEN
        )

    def test_reads_the_tokens_itsdangerous_wrote(self):
        self.assertEqual(tokens.loads(SESSION_TOKEN, SECRET), {"session_id": 7})
        self.assertEqual(
            tokens.loads(LOGIN_TOKEN, SECRET, timed=True, now=ISSUED + 100), {"id": 3}
        )

    def test_expired_login_token_is_refused(self):
        with self.assertRaises(tokens.BadToken):
            tokens.loads(LOGIN_TOKEN, SECRET, timed=True, now=ISSUED + 86401)

    def test_untimed_token_is_refused_where_an_expiry_is_needed(self):
        with self.assertRaises(tokens.BadToken):
            tokens.loads(SESSION_TOKEN, SECRET, timed=True, now=ISSUED)

    def test_other_secret_is_refused(self):
        with self.assertRaises(tokens.BadToken):
            tokens.loads(SESSION_TOKEN, "another-secret")

    def test_changed_payload_is_refused(self):
        header, _, signature = SESSION_TOKEN.split(".")
        forged = ".".join(
            [header, tokens.dumps({"session_id": 8}, SECRET).split(".")[1], signature]
        )
        with self.assertRaises(tokens.BadToken):
            tokens.loads(forged, SECRET)

    def test_malformed_tokens_are_refused(self):
        for token in ["", "abc", "a.b", "a.b.c", SESSION_TOKEN + "x"]:
            with self.subTest(token=token), self.assertRaises(tokens.BadToken):
                tokens.loads(token, SECRET)


if __name__ == "__main__":
    unittest.main()
