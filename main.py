#import paramiko
from utils.config_loader import load_config
from utils.ssh_client import create_ssh_connection
#from utils.screen_orientation import get_screen_orientation
from utils.command_initializer import ensure_all_commands_exist
from utils.send_command import send_command
from utils.device_detector import detect_touch_device
from utils.send_books import send_books
from pynput import keyboard

def make_on_press(config, event):
    def on_press(key):
        try:
            if key in [keyboard.Key.down, keyboard.Key.right, keyboard.Key.up, keyboard.Key.left]:
                ssh = create_ssh_connection(config["kindle_ip"], config["username"], config["password"])
                print("SSH Connection established.")
                if key in [keyboard.Key.down, keyboard.Key.right]:
                    print("Next Page")
                    send_command(ssh, "forward", event)
                elif key in [keyboard.Key.up, keyboard.Key.left]:
                    print("Previous Page")
                    send_command(ssh, "prev", event)
                ssh.close()
            # ==== Press 's' to sync local books to Kindle ====
            elif hasattr(key, 'char') and key.char == 's':
                print("Starting sync...")
                try:
                    send_books(
                        ip=config["kindle_ip"],
                        username=config["username"],
                        password=config["password"],
                        local_dir="books",  # local folder to sync
                        # remote_dir left as default in send_books (Downloads/Items01)
                    )
                except Exception as sync_err:
                    print(f"Sync error: {sync_err}")
            # ==================================================
            elif key == keyboard.Key.esc:
                print("Exiting...")
                return False
            else:
                print("未定义输入")
        except Exception as e:
            print(f"Key handling error: {e}")
    return on_press

if __name__ == "__main__":
    # 从 config/user_config.json 加载 Kindle 连接信息
    try:
        config = load_config("config/user_config.json")
        kindle_ip = config["kindle_ip"]
        username = config["username"]
        password = config["password"]
    except Exception as e:
        print(f"加载配置失败: {e}")
        exit(1)

    # 启动时统一确保命令存在，并在必要时自动检测 event
    ssh = None
    event = None
    try:
        ssh = create_ssh_connection(kindle_ip, username, password)
        print("SSH Connection established.")
        # 无条件确保命令/事件文件存在
        ensure_all_commands_exist(ssh)

        if config.get("event"):
            event = config["event"]
            print(f"✅ 从配置文件使用触控设备: /dev/input/{event}")
        else:
            detected = detect_touch_device(ssh)
            if detected:
                event = detected
                print(f"✅ 自动识别触控设备: /dev/input/{event}")
            else:
                event = "event1"
                print("❌ 自动识别失败，已临时使用默认: /dev/input/event1")
                print("👉 请打开 config/user_config.json，手动添加一行 \"event\": \"eventX\"（例如: \"event\": \"event3\"）")
                print("👉 在 /proc/bus/input/devices 中找到 N: Name=\"pt_mt\" 的块，其下 Handlers=... 中的 eventX 即为正确值")
    except Exception as e:
        print(f"SSH Error: {e}")
        exit(1)
    finally:
        if ssh:
            ssh.close()

    print("Listening for key presses...\n"
          "→ Arrow keys: turn pages\n"
          "→ Press 's' : sync books from ./books to Kindle\n"
          "→ Press ESC : exit")
    with keyboard.Listener(on_press=make_on_press(config, event)) as listener:
        listener.join()
