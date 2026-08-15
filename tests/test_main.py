from app.main import generate_short_code


def test_short_code_length():
    code = generate_short_code()

    assert len(code) == 6


def test_short_code_is_alphanumeric():
    code = generate_short_code()

    assert code.isalnum()
