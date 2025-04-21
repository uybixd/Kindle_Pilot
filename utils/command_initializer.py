from utils.record_event import record_all_commands

def file_exists(ssh, remote_path):
    cmd = f"test -f {remote_path} && echo exists || echo missing"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode().strip() == "exists"

def ensure_all_commands_exist(ssh):
    files = [
        "/mnt/us/FlipCmd/next_portrait.event",
        "/mnt/us/FlipCmd/prev_portrait.event",
        "/mnt/us/FlipCmd/next_landscape.event",
        "/mnt/us/FlipCmd/prev_landscape.event",
    ]

    all_exist = all(file_exists(ssh, f) for f in files)
    if not all_exist:
        print("📂 检测到缺失的翻页命令，准备录制...")
        record_all_commands(ssh)
    else:
        #print("✅ 所有翻页命令均已存在，无需录制。")
        pass