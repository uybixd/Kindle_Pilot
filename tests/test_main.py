import pytest
from unittest.mock import patch, MagicMock
from utils.send_command import send_command

def test_send_command_forward():
    mock_ssh = MagicMock()
    event = "event1"

    mock_stdout = MagicMock()
    mock_stdout.read.return_value = b"success"
    mock_stderr = MagicMock()
    mock_stderr.read.return_value = b""

    mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

    send_command(mock_ssh, "forward", event)

    command = mock_ssh.exec_command.call_args[0][0]
    assert command.startswith("cat /mnt/us/FlipCmd/") and "event1" in command