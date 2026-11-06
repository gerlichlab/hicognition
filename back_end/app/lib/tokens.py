"""Signed tokens for logins and shared sessions, in the format itsdangerous 1.1 wrote them.

itsdangerous 2.1 removed JSONWebSignatureSerializer and TimedJSONWebSignatureSerializer, which
signed these tokens. Session tokens don't expire and are part of the links that share a
session, so this module signs and checks tokens exactly as those classes did, and links shared
before keep working:

- A JSON Web Signature in compact form: header, payload and signature, each base64url-encoded
  without padding, joined by dots. Header and payload are JSON without spaces.
- The signature is HMAC-SHA512 of "header.payload", keyed with the secret key itself: the JWS
  serializers had no salt, which left itsdangerous' key derivation off.
- A login token's header carries the time it was issued (iat) and its expiry (exp), in seconds
  since the epoch; it is refused after its expiry.
"""

import base64
import hashlib
import hmac
import json
import time

ALGORITHM = "HS512"


class BadToken(Exception):
    """The token is malformed, its signature doesn't match, or it has expired."""


def _encode(data: bytes) -> bytes:
    return base64.urlsafe_b64encode(data).rstrip(b"=")


def _decode(data: bytes) -> bytes:
    try:
        return base64.urlsafe_b64decode(data + b"=" * (-len(data) % 4))
    except ValueError as error:
        raise BadToken("not base64url") from error


def _to_json(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _from_json(data: bytes):
    try:
        return json.loads(_decode(data))
    except ValueError as error:
        raise BadToken("not JSON") from error


def _signature(signed: bytes, secret_key: str) -> bytes:
    return _encode(
        hmac.new(secret_key.encode("utf-8"), signed, hashlib.sha512).digest()
    )


def dumps(
    payload: dict,
    secret_key: str,
    expires_in: int | None = None,
    now: int | None = None,
) -> str:
    """Signs payload; with expires_in, the token expires that many seconds after now."""
    header = {"alg": ALGORITHM}
    if expires_in is not None:
        issued = int(time.time()) if now is None else now
        header["iat"] = issued
        header["exp"] = issued + expires_in
    signed = _encode(_to_json(header)) + b"." + _encode(_to_json(payload))
    return (signed + b"." + _signature(signed, secret_key)).decode("ascii")


def loads(
    token: str, secret_key: str, timed: bool = False, now: int | None = None
) -> dict:
    """Returns the payload of a token this module or itsdangerous 1.1 signed with secret_key.

    A timed token must carry an expiry that hasn't passed. Raises BadToken otherwise.
    """
    signed, dot, signature = token.encode("utf-8").rpartition(b".")
    if not dot or not hmac.compare_digest(signature, _signature(signed, secret_key)):
        raise BadToken("signature does not match")
    header, dot, payload = signed.partition(b".")
    if not dot:
        raise BadToken("no payload")
    header = _from_json(header)
    if not isinstance(header, dict) or header.get("alg") != ALGORITHM:
        raise BadToken("unexpected header")
    if timed:
        expiry = header.get("exp")
        if not isinstance(expiry, int) or expiry < 0:
            raise BadToken("no expiry")
        if expiry < (int(time.time()) if now is None else now):
            raise BadToken("expired")
    return _from_json(payload)
