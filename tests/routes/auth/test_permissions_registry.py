from cat.auth.user import User


def test_admin_role_passes_all_checks(client, admin_headers):
    admin = User(id="00000000-0000-0000-0000-000000000000", name="admin", roles=["admin"])

    assert admin.has_role("admin")
    assert admin.has_role("user")  # admin passes all role checks
    assert admin.has_role("anything")
    assert admin.is_admin()


def test_regular_user_role_check(client, admin_headers):
    user = User(id="00000000-0000-0000-0000-000000000000", name="user", roles=["user"])

    assert user.has_role("user")
    assert not user.has_role("admin")
    assert not user.is_admin()


def test_has_role_or_logic(client, admin_headers):
    user = User(id="00000000-0000-0000-0000-000000000000", name="user", roles=["editor"])

    assert user.has_role("editor")
    assert user.has_role("editor", "admin")  # OR logic: has editor
    assert not user.has_role("admin")
    assert not user.has_role("user")
