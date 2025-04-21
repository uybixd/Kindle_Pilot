import time

def prompt_validation():
    print("是否成功翻到下一页？")
    print("1. ✅ 是")
    print("2. ❌ 否")
    print("3. 🤔 没看清楚（再试一次）")
    while True:
        choice = input("请选择 1/2/3，并按回车键确认: ")
        if choice == '1':
            return "yes"
        elif choice == '2':
            return "no"
        elif choice == '3':
            return "retry"

def prompt_yes_no(prompt):
    while True:
        choice = input(prompt + " (y/n): ").lower()
        if choice in ['y', 'n']:
            return choice == 'y'

def record_single_command(ssh, name, remote_path, device="/dev/input/event1", duration=5):
    print(f"\n🟡 请在提示后 {duration} 秒内执行：{name} 的翻页操作")
    print("💡 推荐使用滑动手势进行翻页，以避免误触。你也可以点击屏幕，但滑动更可靠。")
    input("按回车键开始录制...")
    print(f"🎬 正在录制中（将在 {duration} 秒后自动结束）...")
    
    ssh.exec_command("mkdir -p /mnt/us/FlipCmd")
    cmd = f"timeout {duration} cat {device} > {remote_path}"
    ssh.exec_command(cmd)[1].channel.recv_exit_status()
    
    print(f"✅ 已完成录制：{remote_path}")
    while True:
        print("📤 正在尝试发送刚录制的命令以验证效果...")
        ssh.exec_command(f"cat {remote_path} > /dev/input/event1 && /usr/bin/powerd_test -i")[1].channel.recv_exit_status()
        result = prompt_validation()
        if result == "yes":
            break
        elif result == "no":
            return record_single_command(ssh, name, remote_path, device, duration)
        else:
            print("🔁 再次尝试执行命令...")

def record_all_commands(ssh):
    cmd_list = [
        ("竖屏下一页", "/mnt/us/FlipCmd/next_portrait.event"),
        ("竖屏上一页", "/mnt/us/FlipCmd/prev_portrait.event"),
        ("横屏下一页", "/mnt/us/FlipCmd/next_landscape.event"),
        ("横屏上一页", "/mnt/us/FlipCmd/prev_landscape.event"),
    ]
    print("🧭 将引导你录制 4 个翻页命令：\n")
    for name, path in cmd_list:
        record_single_command(ssh, name, path)
    print("\n🎉 所有翻页命令已录制完毕！")