from SV.models import User




def test_new_user():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, hashed_password, and role fields are defined correctly
    """

    user = User('test_user@hello_fp.com', 'test_user', 'test_pass_100')
    assert user.email == 'test_user@hello_fp.com'
    assert user.password_hash != 'test_pass_100'