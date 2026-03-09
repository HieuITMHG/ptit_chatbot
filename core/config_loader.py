import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

class PipelineConfig:

    def __init__(self, path: str):
        config_path = BASE_DIR / path
        print(config_path)

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f) 

    @property
    def chunking(self):
        return self.config.get("chunking", {})