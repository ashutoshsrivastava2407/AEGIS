"""Security Unit Tests for OIDC, SAML 2.0, Local Auth, and Crypto Key Lifecycle."""

import pytest
from services.security.authentication import AuthenticationService


def test_oidc_jwks_protocol_validation():
    auth = AuthenticationService()
    payload = {
        "alg": "RS256",
        "kid": "key-rs256-01",
        "iss": "https://auth.aegis.enterprise",
        "aud": "aegis-app",
        "sub": "user1@aegis.enterprise",
        "exp": 2000000000,
    }
    res = auth.validate_oidc_token(
        id_token="valid.oidc.token",
        expected_issuer="https://auth.aegis.enterprise",
        expected_audience="aegis-app",
        token_payload=payload,
    )
    assert res["valid"] is True
    assert res["subject"] == "user1@aegis.enterprise"


def test_oidc_state_nonce_mismatch_rejection():
    auth = AuthenticationService()
    payload = {
        "alg": "RS256",
        "kid": "key-rs256-01",
        "iss": "https://auth.aegis.enterprise",
        "aud": "aegis-app",
        "sub": "user1@aegis.enterprise",
        "nonce": "correct_nonce",
        "state": "correct_state",
        "exp": 2000000000,
    }
    res_nonce = auth.validate_oidc_token(
        id_token="valid.token",
        expected_issuer="https://auth.aegis.enterprise",
        expected_audience="aegis-app",
        expected_nonce="wrong_nonce",
        token_payload=payload,
    )
    assert res_nonce["valid"] is False
    assert res_nonce["reason"] == "NONCE_MISMATCH"


def test_saml_xml_digital_signature_verification():
    auth = AuthenticationService()
    saml_xml = "<samlp:Response xmlns:samlp='urn:oasis:names:tc:SAML:2.0:protocol'><Assertion>Valid</Assertion></samlp:Response>"
    payload = {
        "signature_valid": True,
        "issuer": "https://idp.aegis.enterprise",
        "audience": "aegis-saml-sp",
        "destination": "https://aegis.enterprise/acs",
    }
    res = auth.validate_saml_assertion(
        saml_xml=saml_xml,
        expected_issuer="https://idp.aegis.enterprise",
        expected_audience="aegis-saml-sp",
        expected_destination="https://aegis.enterprise/acs",
        assertion_payload=payload,
    )
    assert res["valid"] is True
    assert res["issuer"] == "https://idp.aegis.enterprise"


def test_saml_xxe_and_signature_wrapping_defense():
    auth = AuthenticationService()

    # XXE Attack
    xxe_xml = "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]><saml>Evil</saml>"
    res_xxe = auth.validate_saml_assertion(
        saml_xml=xxe_xml,
        expected_issuer="https://idp.aegis.enterprise",
        expected_audience="aegis-saml-sp",
        expected_destination="https://aegis.enterprise/acs",
    )
    assert res_xxe["valid"] is False
    assert res_xxe["reason"] == "XXE_SECURITY_VIOLATION_DETECTED"

    # Signature Wrapping Attack
    wrapped_xml = "<saml>Wrapped</saml>"
    res_wrapped = auth.validate_saml_assertion(
        saml_xml=wrapped_xml,
        expected_issuer="https://idp.aegis.enterprise",
        expected_audience="aegis-saml-sp",
        expected_destination="https://aegis.enterprise/acs",
        assertion_payload={"signature_wrapped": True},
    )
    assert res_wrapped["valid"] is False
    assert res_wrapped["reason"] == "SIGNATURE_WRAPPING_ATTACK_DETECTED"


def test_local_auth_lockout_protection():
    auth = AuthenticationService()
    user_rec = {"id": "u-lock", "tenant_id": "default", "is_active": True, "hashed_password": "hashed_password"}

    for _ in range(5):
        auth.authenticate_credentials("LOCAL", "locked_user", "WrongPassword", user_record=user_rec)

    res = auth.authenticate_credentials("LOCAL", "locked_user", "Password123!", user_record=user_rec)
    assert res["authenticated"] is False
    assert res["reason"] == "ACCOUNT_LOCKED_TEMPORARILY"


def test_session_token_revocation():
    auth = AuthenticationService()
    tok = "active_jwt_token_123"
    payload = {"alg": "RS256", "kid": "key-rs256-01", "iss": "aegis", "aud": "aegis", "exp": 2000000000}

    assert auth.validate_oidc_token(tok, "aegis", "aegis", token_payload=payload)["valid"] is True
    auth.revoke_token(tok)
    assert auth.validate_oidc_token(tok, "aegis", "aegis", token_payload=payload)["valid"] is False


def test_cryptographic_key_rotation_and_jwks_rollover():
    auth = AuthenticationService()
    auth.register_jwk("key-revoked-99", "RS256", "PEM", status="REVOKED")

    payload = {"alg": "RS256", "kid": "key-revoked-99", "iss": "aegis", "aud": "aegis", "exp": 2000000000}
    res = auth.validate_oidc_token("tok", "aegis", "aegis", token_payload=payload)
    assert res["valid"] is False
    assert res["reason"] == "SIGNING_KEY_REVOKED"


def test_crypto_algorithm_confusion_defense():
    auth = AuthenticationService()

    # None algorithm
    res_none = auth.validate_oidc_token("tok", "aegis", "aegis", token_payload={"alg": "none", "kid": "key-rs256-01"})
    assert res_none["valid"] is False
    assert res_none["reason"] == "ALGORITHM_NONE_DISALLOWED"

    # Symmetric HMAC algorithm when asymmetric JWKS expected
    res_hmac = auth.validate_oidc_token(
        "tok", "aegis", "aegis", allow_symmetric_hs256=False, token_payload={"alg": "HS256", "kid": "key-rs256-01"}
    )
    assert res_hmac["valid"] is False
    assert res_hmac["reason"] == "SYMMETRIC_HMAC_DISALLOWED_FOR_ASYMMETRIC_JWKS"
