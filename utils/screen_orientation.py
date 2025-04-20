def get_screen_orientation(ssh):
    import re

    try:
        stdin, stdout, stderr = ssh.exec_command("fbset")
        output = stdout.read().decode().strip()
        #print(f"<<< stdout: {output}")
        match = re.search(r'mode\s+"(\d+)x(\d+)', output)
        if not match:
            raise ValueError("Could not parse resolution")
        width, height = map(int, match.groups())
        return "landscape" if width > height else "portrait"
    except Exception as e:
        return f"SSH Command Error: {e}"