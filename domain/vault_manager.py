import json
import os
import sys
from pathlib import Path
from common.rails_context import RailsContext, railway
from domain.crypto_manager import CryptoManager

class VaultManager:

	def __init__(self):
		os.environ['TERM'] = 'xterm-256color'

	#==============================================
	@railway
	def init(self, context: RailsContext, path):
		print(f"Initializing vault")
		check_path = Path(path)
		if not check_path.exists(): return context.setError(False, f"Vault path '{path}' does not exist")
		password = self.ask_new_password(context)
		keypass = self.generate_keypass(context)
		secret = self.encrypt_secret(context, keypass, password)
		self.save_config(context, path, secret)
		return True

	#==============================================
	@railway
	def read(self, context: RailsContext, path, mkey, params):
		check_path = Path(path)
		if not check_path.exists(): return context.setError(False, f"Vault path '{path}' does not exist")

		print(f"Reading vault. To quit enter empty account ID")
		ask_account = True
		accid = ""
		if 'account' in params:
			accid = params['account']
			ask_account = False

		password = self.ask_password(context)
		keypass = self.get_keypass(context, mkey, password)
		while True:
			if ask_account: accid = input("Enter Account ID: ")
			ask_account = True
			if not accid: break
			self.find_account(context, accid, keypass, path)
			if context.hasError(): break
		return True

	# ------------------------------------
	@railway
	def find_account(self, context: RailsContext, accid, keypass, path):
		if not accid: return context.setError(False, "Missing account ID")
		if not keypass: return context.setError(False, "Missing account ID")
		check_path = Path(path)
		if not check_path.exists(): return context.setError(False, f"Vault path '{path}' does not exist")
		local = RailsContext()
		data = self.read_account(local, accid, path)
		account = self.decrypt_info(local, data, keypass)
		self.display_account(local, account)
		if local.hasError():
			print(f"Account {accid}: {local.error}")
		return True

	#==============================================
	@railway
	def add(self, context: RailsContext, path, mkey, params):
		if not 'account' in params: return context.setError(False, "Missing account")
		if not 'login' in params: return context.setError(False, "Missing login")
		if not 'password' in params: return context.setError(False, "Missing password")

		password = self.ask_password(context)
		keypass = self.get_keypass(context, mkey, password)
		res = self.encrypt_info(context, params['password'], keypass)
		params['password'] = res['data']
		params['hint'] = res['salt']
		self.save_account(context, params, path)
		return True

	#------------------------------------
	@railway
	def ask_password(self, context):
		password = ""
		while not password:
			password = self.safe_input("Enter password (visible): ")
		return password

	#------------------------------------
	@railway
	def ask_new_password(self, context):
		password = input("Enter password (visible): ")
		password2 = input("Enter the password again: ")
		if password != password2: return context.setError(False, "Passwords do not match")
		return password

	#------------------------------------
	@railway
	def generate_keypass(self, context) -> str:
		cm = CryptoManager()
		return cm.generate_password(256)


	#------------------------------------
	@railway
	def encrypt_secret(self, context, keypass: str, password: str):
		if not password: return context.setError(False, "Missing password")
		if not keypass: return context.setError(False, "Missing keypass")
		cm = CryptoManager()
		#encrypt long generated keypass using short password
		res = cm.encrypt(keypass, password, True)
		return res['data']

	#------------------------------------
	@railway
	def encrypt_info(self, context, info: str, password: str):
		if not password: return context.setError(False, "Missing password")
		if not info: return context.setError(False, "Missing data to encrypt")
		cm = CryptoManager()
		return cm.encrypt(info, password)

	#------------------------------------
	@railway
	def save_config(self, context, path, secret):
		check_path = Path(path)
		if not check_path.exists(): return context.setError(False, f"Vault path '{path}' does not exist")
		config_file = {
			"path": path,
			"secret": secret
		}
		with open('config.json', 'w') as json_file:
			json.dump(config_file, json_file, indent=2)

		print(f"Updated config file")


	# ------------------------------------
	@railway
	def save_account(self, context: RailsContext, data, path):
		check_path = Path(path)
		if not check_path.exists(): return context.setError(False, f"Vault path '{path}' does not exist")
		if not 'account' in data: return context.setError(False, "Missing account ID")
		accid = data['account']
		try :
			fname = os.path.join(path, f'{accid}.json')
			with open(fname, 'w') as json_file:
				json.dump(data, json_file, indent=2)
			print(f"Updated account file: {accid}")
		except Exception as e:
			return context.setError(False, f"Cannot save account: {e}")


	# ------------------------------------
	@railway
	def decrypt_info(self, context: RailsContext, data, keypass):
		if not 'hint' in data: return context.setError(False, "Missing hint")
		if not 'password' in data: return context.setError(False, "Missing password")
		salt = data['hint']
		secret = data['password']
		cm = CryptoManager()
		try :
			data['password'] = cm.decrypt(secret, keypass, salt)
		except Exception as e:
			return context.setError(False, f"Invalid password or corrupted data")
		return data

	# ------------------------------------
	@railway
	def display_account(self, context: RailsContext, account):
		if not account: return context.setError(False, "Invalid account")
		if not 'account' in account: return context.setError(False, "Missing account ID")
		print(f"---- {account['account']} ---------------------------")
		if 'login' in account: print(f"Login: {account['login']}")
		if 'password' in account: print(f"Password: {account['password']}")
		if 'url' in account: print(f"URL: {account['url']}")
		print(f"-----------------------------------------------")

	# ------------------------------------
	@railway
	def get_keypass(self, context, mkey, password):
		if not password: return context.setError(False, "Missing password")
		if not mkey: return context.setError(False, "Missing master key")
		cm = CryptoManager()
		try :
			return cm.decrypt(mkey, password)
		except Exception as e:
			return context.setError(False, f"Invalid password or corrupted data")

	# ------------------------------------
	@railway
	def read_account(self, context: RailsContext, accid, path):
		check_path = Path(path)
		if not check_path.exists(): return context.setError(False, f"Vault path '{path}' does not exist")
		fname = os.path.join(path, f'{accid}.json')
		fpath = Path(fname)
		if not fpath.exists(): return context.setError(False, f"Account not found: {accid}")
		with open(fname, 'r') as json_file:
			data = json.load(json_file)
		return data

	# ------------------------------------
	def safe_input(self, prompt=""):
		result = input(prompt)
		sys.stdout.write('\033[1A')
		sys.stdout.write(
			'\033[F                                                                                                           \n')
		sys.stdout.write(
			'                                                                                                           \n')
		sys.stdout.flush()
		return result


	# ------------------------------------
	@railway
	def test_crypto(self, context):
		cm = CryptoManager()
		key = "this-secret-password-sym"
		text = "Mary had a little lamb"
		res = cm.encrypt(text, key)

		salt = res['salt']
		data = res['data']
		print(f"Encrypted: {data}")
		print(f"Salt: {salt}")

		try :
			decrypted = cm.decrypt(data, key, salt)
		except Exception as e:
			return context.setError(False, f"Invalid password or corrupted data")
		if decrypted != text: return context.setError(False, "Encryption failed")
		print(f"Decrypted: {decrypted}")
		return True


