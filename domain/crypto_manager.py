import secrets
import string
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from domain.utils import Utils


class CryptoManager:

	def __init__(self):
		self.base_salt = bytes([87, 38, 13, 24, 69, 11, 7, 15, 22, 35, 18, 21, 87, 78, 64, 21])

	def generate_password(self, length=128):
		characters = string.ascii_letters + string.digits + string.punctuation
		random_string = ''.join(secrets.choice(characters) for i in range(length))
		return random_string

	def encrypt(self, text: str, key: str, use_base = False):
		text_bin = text.encode('utf-8')
		salt = None
		if use_base: salt = self.base_salt
		salt, data = self.__encrypt_bin(text_bin, key, salt)
		return {
			'salt': Utils.bytes_to_str(salt),
			'data': Utils.bytes_to_str(data)
		}

	def decrypt(self, data, key, salt = None) ->str:
		if not salt: salt = Utils.bytes_to_str(self.base_salt)
		salt_bin = Utils.str_to_bytes(salt)
		data_bin = Utils.str_to_bytes(data)
		text_bin = self.__decrypt__bin(data_bin, key, salt_bin)
		return text_bin.decode('utf-8')



	# --- Key Derivation (Password to Key) ---
	def __get_key__bin(self, password:str, salt: bytes) -> bytes:
		"""Derives a key from a password and salt."""
		kdf = PBKDF2HMAC(
			algorithm=hashes.SHA256(),
			length=32,
			salt=salt,
			iterations=480000,
		)
		return base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))

	# --- Encryption ---
	def __encrypt_bin(self, data: bytes, password, salt=None) -> tuple[bytes, bytes]:
		if not salt: salt = secrets.token_bytes(16)
		key = self.__get_key__bin(password, salt)
		return salt, Fernet(key).encrypt(data)

	# --- Decryption ---
	def __decrypt__bin(self, ciphertext: bytes, password, salt: bytes) -> bytes:
		key = self.__get_key__bin(password, salt)
		return Fernet(key).decrypt(ciphertext)