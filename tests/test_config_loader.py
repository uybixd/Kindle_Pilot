import pytest
import os
import json
from utils import config_loader

def test_load_valid_config(tmp_path):
    config_data = {
        "kindle_ip": "192.168.1.100",
        "username": "root",
        "password": "kindle",
        "commands": {
            "portrait": {
                "forward": "echo portrait next",
                "prev": "echo portrait prev"
            },
            "landscape": {
                "forward": "echo landscape next",
                "prev": "echo landscape prev"
            }
        }
    }
    config_file = tmp_path / "valid_config.json"
    config_file.write_text(json.dumps(config_data), encoding="utf-8")

    result = config_loader.load_config(path=str(config_file))
    assert result == config_data

def test_missing_file():
    with pytest.raises(FileNotFoundError):
        config_loader.load_config(path="non_existent_config.json")

def test_invalid_json(tmp_path):
    config_file = tmp_path / "invalid_config.json"
    config_file.write_text("{ invalid json }", encoding="utf-8")

    with pytest.raises(ValueError, match="配置文件格式错误"):
        config_loader.load_config(path=str(config_file))

def test_missing_required_fields(tmp_path):
    config_data = {
        "kindle_ip": "192.168.1.100",
        "username": "root"
        # Missing other required keys
    }
    config_file = tmp_path / "incomplete_config.json"
    config_file.write_text(json.dumps(config_data), encoding="utf-8")

    with pytest.raises(ValueError, match="配置文件缺少字段"):
        config_loader.load_config(path=str(config_file))
