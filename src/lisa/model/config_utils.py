import os
import copy
import json

from typing import Any, Dict, Union

from src.lisa.utils.logmanager import get_logger
CONFIG_NAME = "config.json"
logger = get_logger(__name__)


class Config():
    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except AttributeError as err:
                logger.error(f"Can't set {key} with value {value} for {self}")
                raise err

    def save_pretrained(self, save_directory):
        if os.path.isfile(save_directory):
            raise AssertionError(f"Provided path ({save_directory}) should be a directory, not a file")
        os.makedirs(save_directory, exist_ok=True)
        # If we save using the predefined names, we can load using `from_pretrained`
        output_config_file = os.path.join(save_directory, CONFIG_NAME)

        self.to_json_file(output_config_file)
        logger.info(f"Configuration saved in {output_config_file}")

    @classmethod
    def from_json_file(cls, json_file: Union[str, os.PathLike]) -> "Config":
        config_dict = cls._dict_from_json_file(json_file)
        return cls(**config_dict)

    @classmethod
    def _dict_from_json_file(cls, json_file: Union[str, os.PathLike]):
        with open(json_file, "r", encoding="utf-8") as reader:
            text = reader.read()
        return json.loads(text)

    def to_json_file(self, json_file_path):
        with open(json_file_path, "w", encoding="utf-8") as writer:
            writer.write(self.to_json_string())

    def to_json_string(self) -> str:
        config_dict = self.to_dict()
        return json.dumps(config_dict, indent=2, sort_keys=True) + "\n"

    def to_dict(self) -> Dict[str, Any]:
        output = copy.deepcopy(self.__dict__)
        if hasattr(self.__class__, "model_type"):
            output["model_type"] = self.__class__.model_type
        return output

    def update(self, config_dict):
        for key, value in config_dict.items():
            setattr(self, key, value)

    def update_key_value(self, key, value):
        setattr(self, key, value)
