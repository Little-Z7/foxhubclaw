from foxhubclaw.crypto import decrypt_secret, encrypt_secret, mask_key


def test_encrypt_roundtrip():
    token = encrypt_secret("ak_secret_value", "unit-test-secret-key-32bytes!!")
    assert token != "ak_secret_value"
    assert decrypt_secret(token, "unit-test-secret-key-32bytes!!") == "ak_secret_value"


def test_mask_key_keeps_last_four():
    assert mask_key("ak_abcdef1234") == "••••1234"
    assert mask_key("") == ""
