#import paramiko
import time
import threading
import queue
from utils.config_loader import load_config
from utils.ssh_client import create_ssh_connection
#from utils.screen_orientation import get_screen_orientation
from utils.command_initializer import ensure_all_commands_exist
from utils.send_command import send_command
from utils.device_detector import detect_touch_device
from utils.send_books import send_books
from pynput import keyboard

def make_on_press(config, event, cmd_queue, min_interval=0.3):
    ARROWS = {keyboard.Key.down, keyboard.Key.right, keyboard.Key.up, keyboard.Key.left}

    def on_press(key):
        try:
            if key in ARROWS:
                # Enqueue command; worker will rate-limit between sends
                if key in (keyboard.Key.down, keyboard.Key.right):
                    cmd_queue.put("forward")
                    # print("→ queued: forward")
                elif key in (keyboard.Key.up, keyboard.Key.left):
                    cmd_queue.put("prev")
                    # print("→ queued: prev")
                return

            if hasattr(key, 'char') and key.char == 's':
                print("Starting sync...")
                try:
                    send_books(
                        ip=config["kindle_ip"],
                        username=config["username"],
                        password=config["password"],
                        local_dir="books",
                    )
                except Exception as sync_err:
                    print(f"Sync error: {sync_err}")
                return

            if key == keyboard.Key.esc:
                print("Exiting...")
                return False
            else:
                print("未定义输入")
        except Exception as e:
            print(f"Key handling error: {e}")
    return on_press

def start_command_worker(config, event, cmd_queue, running_flag, min_interval=0.45):
    def worker():
        while running_flag[0]:
            try:
                cmd = cmd_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            try:
                ssh = create_ssh_connection(config["kindle_ip"], config["username"], config["password"])
                print("SSH Connection established.")
                if cmd == "forward":
                    print("Next Page")
                    send_command(ssh, "forward", event)
                elif cmd == "prev":
                    print("Previous Page")
                    send_command(ssh, "prev", event)
            except Exception as e:
                print(f"Worker error: {e}")
            finally:
                try:
                    ssh.close()
                except Exception:
                    pass
                # Rate-limit between consecutive commands
                time.sleep(min_interval)
                cmd_queue.task_done()
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    return t

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
    # Set up producer-consumer: key events -> queue -> worker -> Kindle
    cmd_queue = queue.Queue()
    running_flag = [True]
    worker_thread = start_command_worker(config, event, cmd_queue, running_flag, min_interval=0.45)

    try:
        with keyboard.Listener(on_press=make_on_press(config, event, cmd_queue, min_interval=0.45)) as listener:
            listener.join()
    finally:
        # Stop worker and drain any remaining tasks before exit
        running_flag[0] = False
        # Wait for queued tasks to finish (optional timeout could be added)
        try:
            cmd_queue.join()
        except Exception:
            pass
