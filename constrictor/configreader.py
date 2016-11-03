import json

from os import environ
from os.path import dirname, join
from string import Template

PARENT_PATH_KEY = "parent"
EXTRA_CONTROL_FIELDS_KEY = "extra_control_fields"

try:
    basestring


    def is_str(s):
        return isinstance(s, basestring)
except NameError:
    def is_str(s):
        return isinstance(s, str)


class ConfigReader(object):
    def __init__(self, config_path):
        self.config_path = config_path

    @staticmethod
    def read_json(path):
        with open(path) as config_fp:
            return json.load(config_fp)

    def load_config_file(self, config_path):
        config = self.read_json(config_path)
        self.add_parent_config(config_path, config)
        self.interpolate_environment_variables_in_dict(config)
        return config

    @staticmethod
    def parse_environment_variable_value(value):
        t = Template(value)
        return t.substitute(environ)

    def interpolate_environment_variables_in_list(self, value_list):
        for index, value in enumerate(value_list):
            if isinstance(value, dict):
                self.interpolate_environment_variables_in_dict(value)
            elif isinstance(value, list):
                self.interpolate_environment_variables_in_list(value)
            elif is_str(value):
                value_list[index] = self.parse_environment_variable_value(value)

    def interpolate_environment_variables_in_dict(self, value_dict):
        for key, value in value_dict.items():
            if isinstance(value, dict):
                self.interpolate_environment_variables_in_dict(value)
            elif isinstance(value, list):
                self.interpolate_environment_variables_in_list(value)
            elif is_str(value):
                value_dict[key] = self.parse_environment_variable_value(value)

    def add_parent_config(self, current_config_path, config):
        if PARENT_PATH_KEY in config:
            parent_path = join(dirname(current_config_path), config[PARENT_PATH_KEY])
            parent_config = self.read_json(current_config_path)
            self.add_parent_config(parent_path, parent_config)

            for key, value in parent_config.items():
                if key == PARENT_PATH_KEY:
                    continue

                if key not in config:
                    config[key] = value
                elif key == EXTRA_CONTROL_FIELDS_KEY:
                    for cf_key, cf_value in parent_config[key].items():
                        if cf_key not in config[key]:
                            config[key][cf_key] = cf_value
