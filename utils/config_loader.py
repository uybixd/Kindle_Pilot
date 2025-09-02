import os
import sys
import json
import re


def resource_path(relative_path):
    """Get absolute path to resource, based on main script location."""
    if getattr(sys, 'frozen', False):
        # If bundled by PyInstaller
        base_path = os.path.dirname(sys.executable)
    else:
        # If running from source
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_path, relative_path)


def load_config(path="config/user_config.json"):
    full_path = resource_path(path)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"配置文件 {full_path} 未找到")
    except json.JSONDecodeError as e:
        raise ValueError(f"配置文件格式错误：{e}")

    required_keys = ["kindle_ip", "username", "password"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"配置文件缺少字段: {key}")

    # 可选字段：event（例如 "event4"）。如果提供则校验格式；未提供则设为 None，
    # 让上游逻辑决定是否跳过自动识别。
    event_val = config.get("event")
    if event_val is None or event_val == "":
        config["event"] = None
    else:
        if not re.match(r"^event\d+$", str(event_val)):
            raise ValueError("配置文件字段 event 格式应为 'eventX'，例如 'event4'")

    return config