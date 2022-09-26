import yaml
from pathlib import Path
import os

class ConfigFile:
    def __init__(self,env) -> None:
        # Get the root path of config.yaml
        self.path = Path(__file__).parents[2]
        self.config_file = open(f'{self.path}/config.{env}.yaml',mode='r',encoding='utf-8')
        self.config = yaml.load(self.config_file,Loader=yaml.FullLoader)

try:
    env = os.environ["env"]
except:
    env = "dev"
config = ConfigFile(env).config