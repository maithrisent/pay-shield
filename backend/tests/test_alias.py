from services.alias_service import generate_alias_string, get_or_create_alias

def test_generate_alias_format():
    alias = generate_alias_string()
    assert alias.endswith("@payshield")
    assert len(alias.split("@")[0]) == 8

def test_reuse_returns_same_alias(db_cursor, user_a, user_b):
    first = get_or_create_alias(db_cursor, user_a, user_b)
    second = get_or_create_alias(db_cursor, user_a, user_b)
    assert first == second