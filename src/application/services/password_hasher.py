import bcrypt

from src.domain.interfaces.password_hasher_interface import IPasswordHasher


class BcryptPasswordHasher(IPasswordHasher):
    """Implementation of hashed_password hasher using bcrypt algorithm."""
    def verify(self, plain_password: str, password_hash: str) -> bool:
        # bcrypt expects bytes, so we encode our strings
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            password_hash.encode('utf-8')
        )

    def hash(self, password: str) -> str:
        # Generate a salt and hash the hashed_password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')