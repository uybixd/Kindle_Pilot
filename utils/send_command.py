from utils.screen_orientation import get_screen_orientation

def send_command(ssh, action, event):
    """
    根据屏幕方向和操作类型，通过 SSH 发送命令，不再依赖 config 中的命令字段。

    参数:
        ssh: 已建立的 paramiko SSHClient 连接
        action: 操作类型，通常是 "forward" 或 "prev"
        event: 已识别的 event 名称，如 "event1"
    """
    try:
        direction = get_screen_orientation(ssh)

        event_map = {"forward": "next", "prev": "prev"}
        event_name = event_map.get(action, action)
        event_file = f"/mnt/us/FlipCmd/{event_name}_{direction}.event"
        command = f"cat {event_file} > /dev/input/{event}"
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
            print(f"Output: {output}")
        if error:
            print(f"Error: {error}")
    except Exception as e:
        print(f"SSH Command Error: {e}")
