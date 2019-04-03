import yaml


def load_config(config_file='config.yml'):
    with open(config_file, 'r') as cfg:
        return yaml.load(cfg) if cfg else {}


CONFIG = load_config()
