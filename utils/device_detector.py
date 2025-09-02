import re
import json
import os
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
        print(f"[调试] 标准输出:\n{output}")
        # print(f"[调试] 错误输出:\n{err_output}")
        
        event_device = extract_event_device(output)
        if event_device:
            print(f"✅ 自动识别触控设备: /dev/input/{event_device}")
            _persist_event_to_config(event_device)
            return event_device
        else:
            # print(f"[调试] 识别失败")
            print("❌ 自动识别失败，已切换为手动输入模式。如您愿意，请将设备名称反馈给开发者以便支持更多机型。")
            return None
    except Exception as e:
        print(f"❌ 识别设备时出错: {e}")
        return None

def extract_event_device(text):
    # --- Strategy 1: Robust forward-scan from the "pt_mt" device name ---
    # We scan lines; when we see `N: Name="pt_mt"`, we look forward until the
    # next device block (a line starting with `I:`) and return the first
    # eventX we encounter (ideally from a `H: Handlers=` line).
    lines = [ln.strip() for ln in text.splitlines()]

    for idx, ln in enumerate(lines):
        if 'N: Name="pt_mt"' in ln:
            j = idx + 1
            while j < len(lines) and not lines[j].startswith('I:'):
                # Prefer event from a Handlers line
                m = re.search(r"H:\s*Handlers=.*?(event\d+)", lines[j])
                if m:
                    return m.group(1)
                # Otherwise accept any eventX on the line
                m2 = re.search(r"(event\d+)", lines[j])
                if m2:
                    return m2.group(1)
                j += 1
            # If we didn't find any eventX before the next block, keep searching

    # --- Strategy 2 (fallback): original block parsing with pt_mt + ABS ---
    blocks = []
    current_block = []

    for line in lines:
        if line.startswith("I:"):
            if current_block:
                blocks.append(current_block)
            current_block = [line]
        else:
            current_block.append(line)
    if current_block:
        blocks.append(current_block)

    for block in blocks:
        has_pt_mt = any('N: Name="pt_mt"' in line for line in block)
        has_abs = any(line.startswith("B: ABS=") for line in block)
        if has_pt_mt and has_abs:
            for line in block:
                if line.startswith("H: Handlers="):
                    match = re.search(r"(event\d+)", line)
                    if match:
                        return match.group(1)

    return None

def _persist_event_to_config(event_str, config_path="config/user_config.json"):
    """将识别到的 event 写入到配置文件中的 `event` 字段。
    - 若配置文件不存在：创建并仅写入 event（不覆盖你已有的加载校验逻辑）。
    - 若存在：加载 JSON，保留其他字段，只更新/新增 `event`。
    - 操作失败时仅打印警告，不中断主流程。
    """
    try:
        # 确保配置目录存在
        os.makedirs(os.path.dirname(config_path) or ".", exist_ok=True)

        data = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"⚠️ 无法读取配置文件（将创建新文件）: {e}")
                data = {}

        data["event"] = event_str
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"💾 已写入配置文件: {config_path} → event={event_str}")
    except Exception as e:
        print(f"⚠️ 无法写入配置文件: {e}")