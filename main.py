#import paramiko
from utils.config_loader import load_config
from utils.ssh_client import create_ssh_connection
#from utils.screen_orientation import get_screen_orientation
from utils.command_initializer import ensure_all_commands_exist
from utils.send_command import send_command
from utils.device_detector import detect_touch_device
from pynput import keyboard

ssh = None
event = None  # 新增变量

def on_press(key):
    try:
        if key == keyboard.Key.down or key == keyboard.Key.right:
            print("Next Page")
            send_command(ssh, "forward", event)
        elif key == keyboard.Key.up or key == keyboard.Key.left:
            print("Previous Page")
            send_command(ssh, "prev", event)
        elif key == keyboard.Key.esc:
            print("Exiting...")
            ssh.close()  # 关闭 SSH 连接
            return False  # 退出监听
    except AttributeError:
        pass

if __name__ == "__main__":
    # 从 config/config.json 加载 Kindle 连接信息
    try:
        config = load_config()
        kindle_ip = config["kindle_ip"]
        username = config["username"]
        password = config["password"]
    except Exception as e:
        print(f"加载配置失败: {e}")
        exit(1)

    # 创建 SSH 连接
    try:
        ssh = create_ssh_connection(kindle_ip, username, password)
        print("SSH Connection established.")
        ensure_all_commands_exist(ssh)
        event = detect_touch_device(ssh)  # 初始化一次 event
        if not event:
            event = input("未能自动识别触控设备，请手动输入（如 event1）: ").strip()
    except Exception as e:
        print(f"SSH Error: {e}")
        exit(1)  # 连接失败直接退出

    print("Listening for key presses... Press ESC to exit.")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
