import os
import yaml
from linkinpark.lib.common.logger import getLogger

def interpolate(config, environment):
    for key, value in config.items():
        if isinstance(value, str):
            config[key] = value.format(**environment)
        elif isinstance(value, dict):
            interpolate(value, environment)

def load_yaml_with_environment(filename, environment):
    with open(filename, 'r') as file:
        config = yaml.safe_load(file)
    interpolate(config, environment)
    return config

# Load configuration
APP_ENV = os.environ.get("APP_ENV", "dev")

SERVICE_LOGGER = getLogger(
    name="ai-llm-service",
    labels={"env": APP_ENV}
)

current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "config", "server_init_local.yaml")

if not os.path.exists(config_path):
    raise FileNotFoundError(f"Configuration file not found: {config_path}")

server_init_config = load_yaml_with_environment(config_path, {'APP_ENV': APP_ENV})
