#import paramiko
from utils.config_loader import load_config
from utils.ssh_client import create_ssh_connection
from utils.screen_orientation import get_screen_orientation
from pynput import keyboard

ssh = None

def send_command(action):
    try:
        direction = get_screen_orientation(ssh)
        #print(f">>> direction name: {direction}")
        command = config["commands"][direction][action]
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
            print(f"Output: {output}")
        if error:
            print(f"Error: {error}")

    except Exception as e:
        print(f"SSH Command Error: {e}")

def on_press(key):
    try:
        if key == keyboard.Key.down or key == keyboard.Key.right:
            print("Next Page")
            send_command("forward")
        elif key == keyboard.Key.up or key == keyboard.Key.left:
            print("Previous Page")
            send_command("prev")
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
    except Exception as e:
        print(f"SSH Error: {e}")
        exit(1)  # 连接失败直接退出

    print("Listening for key presses... Press ESC to exit.")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
