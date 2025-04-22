import pytest
from unittest.mock import patch, MagicMock
import main  # 如果项目结构支持，可以改为 from Kindle_Helper import main

def test_send_command_forward():
    with patch.object(main, "event", "event1"), \
         patch.object(main, "ssh") as mock_ssh:

        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"success"
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""

        mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

        main.send_command(main.ssh, "forward", main.event)

        assert mock_ssh.exec_command.call_args[0][0].startswith("cat /mnt/us/FlipCmd/")