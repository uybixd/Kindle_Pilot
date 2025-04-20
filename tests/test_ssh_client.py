from unittest.mock import patch, MagicMock
from utils.ssh_client import create_ssh_connection

def test_create_ssh_connection():
    with patch("utils.ssh_client.paramiko.SSHClient") as MockSSHClient:
        mock_ssh_instance = MagicMock()
        MockSSHClient.return_value = mock_ssh_instance

        ip = "192.168.1.100"
        username = "root"
        password = "kindle"

        ssh = create_ssh_connection(ip, username, password)

        # 检查 paramiko.SSHClient() 被调用
        MockSSHClient.assert_called_once()

        # 检查 connect() 被正确调用
        mock_ssh_instance.connect.assert_called_once_with(
            ip, username=username, password=password
        )

        # 返回值是否是我们 mock 出来的对象
        assert ssh == mock_ssh_instance