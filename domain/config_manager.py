import json
import sys
from pathlib import Path
from common.rails_context import RailsContext, railway


class ConfigManager:

	@railway
	def load(self, context: RailsContext):
		config_path = Path("config.json")

		try:
			if not config_path.exists():
				econfig = {
					"path": "./",
					"secret": "?"
				}
				config_path.write_text(json.dumps(econfig, indent=2) + "\n", encoding="utf-8")

			with open('config.json', 'r') as json_file:
				self.config = json.load(json_file)

			if not isinstance(self.config, dict):
				return context.setError(False, "config.json must contain a JSON object at the top level")
			self.path = self.config['path']
			self.secret = self.config['secret']

			return True
		except OSError as e:
			return context.setError(False, f"Failed to create/read config.json: {e}")

		return True

	@railway
	def read_cmd_line(self, context: RailsContext):

		self.params = {}
		if len(sys.argv) < 2:
			return context.setError(False, "Missing command")
		self.command = sys.argv[1]
		if self.command not in ["-init", "-add", "-read"]:
			return context.setError(False, "Invalid command")

		for i in range(2, len(sys.argv)):
			match i:
				case 2: self.params['account'] = sys.argv[i]
				case 3: self.params['login'] = sys.argv[i]
				case 4: self.params['password'] = sys.argv[i]
				case 5: self.params['url'] = sys.argv[i]
		return True