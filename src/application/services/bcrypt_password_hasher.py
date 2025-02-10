from src.domain.interfaces.IPasswordHasher import IPasswordHasher


class BcryptPasswordHasher(IPasswordHasher):
    """Implementation of password hasher using bcrypt algorithm."""

    def verify(self, plain_password: str, password_hash: str, bcrypt=None) -> bool:
        # bcrypt expects bytes, so we encode our strings
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            password_hash.encode('utf-8')
        )

    def hash(self, password: str, bcrypt=None) -> str:
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')