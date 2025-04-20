import pytest
from unittest.mock import patch, MagicMock
import main  # 你可能需要改成 from Kindle_Helper import main

def test_send_command_forward():
    # 模拟方向为 portrait，配置中也提供命令
    with patch("main.get_screen_orientation", return_value="portrait"), \
         patch.object(main, "ssh") as mock_ssh:

        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"success"
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""

        mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

        main.config = {
            "commands": {
                "portrait": {
                    "forward": "echo forward",
                    "prev": "echo prev"
                }
            }
        }

        main.send_command("forward")

        mock_ssh.exec_command.assert_called_with("echo forward")