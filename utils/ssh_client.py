# utils/ssh_client.py
import paramiko


def create_ssh_connection(
    ip,
    username,
    password,
    port: int = 22,
    key_filename: str | None = None,
    pkey: paramiko.PKey | None = None,
    timeout: int = 10,
    allow_agent: bool = True,
    look_for_keys: bool = True,
    keepalive: int | None = 30,
):
    """Create and return a connected paramiko.SSHClient.

    Args:
        ip: Host/IP of the Kindle.
        username: SSH username (Kindle 通常为 'root').
        password: Password (USBNet 常为空字符串 '').
        port: SSH port (default 22).
        key_filename: Path to private key file (optional).
        pkey: Loaded paramiko.PKey object (optional).
        timeout: Socket timeout in seconds.
        allow_agent: Use SSH agent if available.
        look_for_keys: Search for keys in ~/.ssh.
        keepalive: If set, send keepalive every N seconds.
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        ip,
        port=port,
        username=username,
        password=password,
        key_filename=key_filename,
        pkey=pkey,
        timeout=timeout,
        allow_agent=allow_agent,
        look_for_keys=look_for_keys,
    )
    if keepalive and ssh.get_transport():
        ssh.get_transport().set_keepalive(keepalive)
    return ssh


def create_sftp_client(
    ip,
    username,
    password,
    port: int = 22,
    **kwargs,
):
    """Return (sftp, ssh) tuple for convenience."""
    ssh = create_ssh_connection(ip, username, password, port=port, **kwargs)
    sftp = ssh.open_sftp()
    return sftp, ssh


def close_ssh(ssh=None, sftp=None):
    """Gracefully close SFTP then SSH (ignore errors)."""
    try:
        if sftp:
            sftp.close()
    finally:
        if ssh:
            ssh.close()