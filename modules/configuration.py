import json
import os
from functools import reduce

from typing import Any, List, Dict, Tuple


class Configuration:
    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.config = {}
        self._default_config = {}
        if self.file_exists(config_file_path):
            with open(self.config_file_path, "r") as config_file_object:
                self.config = json.load(config_file_object)
                config_file_object.close()

    @staticmethod
    def file_exists(file_path: str):
        return os.path.exists(file_path)

    def read(self, keys: List[Any]) -> Any:
        config = self.config
        for key in keys:
            if key not in config:
                return None
            config = config[key]
        return config

    def write(self, keys: List[Any] | str, value: Any):
        if isinstance(keys, str):
            self.config[keys] = value
            return self
        for key in keys[:-1]:
            if key not in self.config:
                self.config[key] = {}
            self.config = self.config[key]
        self.config[keys[-1]] = value
        return self

    def write_dict(self, to_write: dict):
        for key, value in to_write.items():
            self.write(key, value)
        return self

    def flush(self):
        with open(self.config_file_path, "w+") as config_file_object:
            config_file_object.write(
                json.dumps(self.config, indent=2, ensure_ascii=False)
            )
            config_file_object.close()
        return self

    def set_default(self, default: dict):
        self._default_config = default
        return self

    def write_defaults(self):
        return self.write_dict(self._default_config)


def get_by_path(root: Dict[str, Any], items: List[str]) -> Any:
    """Get a value from a nested dictionary given a list of keys."""
    return reduce(lambda d, key: d.get(key, {}), items, root)


def set_by_path(root: Dict[str, Any], items: List[str], value: Any) -> None:
    """Set a value in a nested dictionary given a list of keys."""
    for item in items[:-1]:
        root = root.setdefault(item, {})
    root[items[-1]] = value


def check_missing_keys(
        config_data: Dict[str, Any],
        default_data: Dict[str, Any],
        path: List[str] = None,
        ignore_paths: List[List[str]] = None
) -> Tuple[Dict[str, Any], List[str]]:
    """Check missing keys in configuration data and return new config and missing keys"""
    if path is None:
        path = []
    if ignore_paths is None:
        ignore_paths = []

    def is_path_ignored(check_path: List[str]) -> bool:
        return any(check_path[:len(ignore_path)] == ignore_path for ignore_path in ignore_paths)

    missing_elements: List[str] = []
    updated_config: Dict[str, Any] = {}
    for key, default in default_data.items():
        current_path = path + [key]
        if is_path_ignored(current_path):
            continue

        if isinstance(default, dict):
            nested_config, nested_missing = check_missing_keys(
                config_data.get(key, {}), default, current_path, ignore_paths)
            if nested_missing:
                missing_elements.extend(nested_missing)
            updated_config[key] = nested_config
        else:
            try:
                nested_value = get_by_path(config_data, current_path)
            except KeyError:
                nested_value = None

            if nested_value is None:
                set_by_path(config_data, current_path, default)
                missing_elements.append("/".join(map(str, current_path)))
            updated_config[key] = nested_value if nested_value is not None else default

    return updated_config, missing_elements
