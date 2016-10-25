import json

from os.path import dirname, join

PARENT_PATH_KEY = "parent"
EXTRA_CONTROL_FIELDS_KEY = "extra_control_fields"


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
        return config

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
