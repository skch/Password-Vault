from common.rails_context import RailsContext, railway
from domain.config_manager import ConfigManager
from domain.vault_manager import VaultManager


def print_usage():
	print("Usage: ")
	print("   python the-vault.py -read {account}")
	print("                  -add {account} {login} {password} {url}")


def main():
	print("Password vault (skch@usa.net) 1.02")
	context = RailsContext()
	cfg = ConfigManager()
	if not cfg.read_cmd_line(context):  print_usage()
	cfg.load(context)
	pm = VaultManager()
	match cfg.command:
		case "-init":
			pm.init(context, cfg.path)
		case "-read":
			pm.read(context, cfg.path, cfg.secret, cfg.params)
		case "-add":
			pm.add(context, cfg.path, cfg.secret, cfg.params)
		case _:
			print("The command is not implemented yet.")

	if (context.hasError()):
		print(f"ERROR: {context.error}")


if __name__ == "__main__":
	main()
