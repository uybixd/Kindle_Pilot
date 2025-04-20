import json


def load_config(path="./config/user_config.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"配置文件 {path} 未找到")
    except json.JSONDecodeError as e:
        raise ValueError(f"配置文件格式错误：{e}")

    required_keys = ["kindle_ip", "username", "password", "commands"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"配置文件缺少字段: {key}")

    for orientation in ["portrait", "landscape"]:
        if orientation not in config["commands"]:
            raise ValueError(f"配置文件缺少命令组: {orientation}")
        for cmd_key in ["forward", "prev"]:
            if cmd_key not in config["commands"][orientation]:
                raise ValueError(f"配置文件中 {orientation} 缺少命令: {cmd_key}")

    return config