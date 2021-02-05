import json
from logging import getLevelName
from shutil import copyfile

from util.log import Log
from util.resource import *
from util.singleton import Singleton

config_path = get_data_path('DreamAPI.json')


class Config(metaclass=Singleton):
	# Type annotation for IDE hinting
	port: int
	log_level: str
	start_minimized: bool
	block_telemetry: bool

	def __init__(self):
		# Load config dictionaries
		saved = self.__get_config_json()
		default = self.__get_bundle_json()

		# Extract version info
		saved_version = saved['config_version']
		default_version = default['config_version']

		# Assign json properties to the class instance
		self.__keys = ['port', 'log_level', 'start_minimized', 'block_telemetry']
		for key in self.__keys:
			# Try saved value first, otherwise use default
			try:
				self.__setattr__(key, saved[key])
			except KeyError:
				self.__setattr__(key, default[key])

		# Get the latest version
		self.config_version: int = default_version

		# Save the new fields
		if saved_version < default_version:
			self.__save_config_file(default_version)

		# Update the log level since we know now the preference
		Log().setLevel(getLevelName(self.log_level))
		Log().debug(f'Setting log level to {self.log_level}')

	@staticmethod
	def __get_config_json() -> dict:
		if is_production and not config_path.exists():
			orig_config = get_bundle_path('DreamAPI.json')
			copyfile(orig_config, config_path)

		with open(config_path) as file:
			return json.load(file)

	@staticmethod
	def __get_bundle_json() -> dict:
		orig_config = get_bundle_path('DreamAPI.json')
		with open(orig_config) as file:
			return json.load(file)

	def __save_config_file(self, version: int):
		json_dict = {key: self.__getattribute__(key) for key in self.__keys}
		json_dict['config_version'] = version

		with open(config_path, 'w') as writer:
			writer.write(json.dumps(json_dict, indent=2))

		Log().warning(f'Updated the config file with new properties')