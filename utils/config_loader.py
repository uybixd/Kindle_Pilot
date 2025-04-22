import json


def load_config(path="./config/user_config.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"配置文件 {path} 未找到")
    except json.JSONDecodeError as e:
        raise ValueError(f"配置文件格式错误：{e}")

    required_keys = ["kindle_ip", "username", "password"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"配置文件缺少字段: {key}")

    return config