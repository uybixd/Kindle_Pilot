import re
def detect_touch_device(ssh):
    """
    自动识别 Kindle 上的触控设备（基于具有 ABS 能力的输入设备）
    返回 eventX 字符串，例如 event1；若失败返回 None。
    """
    cmd = "cat /proc/bus/input/devices"

    try:
        stdin, stdout, stderr = ssh.exec_command(cmd)

        output = stdout.read().decode().strip()
        err_output = stderr.read().decode().strip()
        # print(f"[调试] 标准输出:\n{output}")
        # print(f"[调试] 错误输出:\n{err_output}")
        
        event_device = extract_event_device(output)
        if event_device:
            print(f"✅ 自动识别触控设备: /dev/input/{event_device}")
            return event_device
        else:
            # print(f"[调试] 识别失败")
            print("❌ 自动识别失败，已切换为手动输入模式。如您愿意，请将设备名称反馈给开发者以便支持更多机型。")
            return None
    except Exception as e:
        print(f"❌ 识别设备时出错: {e}")
        return None

def extract_event_device(text):
    blocks = []
    current_block = []

    for line in text.splitlines():
        line = line.strip()
        if line.startswith("I:"):
            if current_block:
                blocks.append(current_block)
            current_block = [line]
        else:
            current_block.append(line)
    if current_block:
        blocks.append(current_block)

    for block in blocks:
        # print(f"<<<< block: {block}")
        has_pt_mt = any('N: Name="pt_mt"' in line for line in block)
        has_abs = any(line.startswith("B: ABS=") for line in block)
        if has_pt_mt and has_abs:
            for line in block:
                if line.startswith("H: Handlers="):
                    match = re.search(r"(event\d+)", line)
                    # print(f">>>> match {match}")
                    if match:
                        return match.group(1)
    return None