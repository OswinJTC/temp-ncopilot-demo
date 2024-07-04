
import yaml

def interpolate(config, environment):
    for key, value in config.items():
        if isinstance(value, str):
            config[key] = value.format(**environment)
        elif isinstance(value, dict):
            interpolate(value)

def load_yaml_with_environment(filename, environment):
    with open(filename, 'r') as file:
        config = yaml.safe_load(file)

    interpolate(config, environment)
    return config

