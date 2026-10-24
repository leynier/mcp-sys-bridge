"""Exercise security fixes whose upstream advisory metadata is incomplete."""

from collections.abc import Callable
from typing import Any

import jwt
import pytest
from jwt.utils import base64url_encode


@pytest.mark.parametrize("decode", [jwt.decode, jwt.decode_complete])
def test_jwt_options_reuse_preserves_claim_verification(
    decode: Callable[..., Any],
) -> None:
    secret = "local-test-key-with-at-least-32-bytes"
    token = jwt.encode({"sub": "test", "exp": 1}, secret, algorithm="HS256")
    options = {"verify_signature": False}

    decode(token, options=options)

    assert options == {"verify_signature": False}
    options["verify_signature"] = True
    with pytest.raises(jwt.ExpiredSignatureError):
        decode(token, secret, algorithms=["HS256"], options=options)
    assert options == {"verify_signature": True}


@pytest.mark.parametrize("use_jwks_client", [False, True])
def test_deep_jwt_payload_raises_documented_decode_error(
    use_jwks_client: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The native JSON parser's recursion limit can exceed sys.getrecursionlimit().
    depth = 200_000
    header = base64url_encode(b'{"alg":"HS256","kid":"test"}')
    payload = base64url_encode(b"[" * depth + b"]" * depth)
    token = b".".join((header, payload, base64url_encode(b"signature"))).decode()

    if use_jwks_client:
        client = jwt.PyJWKClient("https://jwks.invalid/keys")
        monkeypatch.setattr(
            client,
            "fetch_data",
            lambda: pytest.fail("Malformed tokens must fail before fetching JWKS"),
        )
        with pytest.raises(jwt.DecodeError):
            client.get_signing_key_from_jwt(token)
    else:
        with pytest.raises(jwt.DecodeError):
            jwt.decode(token, options={"verify_signature": False})
