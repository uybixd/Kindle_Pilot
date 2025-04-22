import pytest
from unittest.mock import patch, MagicMock
from utils import send_command

@patch("utils.send_command.get_screen_orientation", return_value="portrait")
def test_send_command_forward(mock_orientation):
    ssh_mock = MagicMock()
    stdout_mock = MagicMock()
    stderr_mock = MagicMock()
    stdout_mock.read.return_value = b""
    stderr_mock.read.return_value = b""
    ssh_mock.exec_command.return_value = (None, stdout_mock, stderr_mock)

    send_command.send_command(ssh_mock, "forward", "event1")
    expected_file = "/mnt/us/FlipCmd/next_portrait.event"
    expected_command = f"cat {expected_file} > /dev/input/event1"

    ssh_mock.exec_command.assert_called_with(expected_command)

@patch("utils.send_command.get_screen_orientation", return_value="landscape")
def test_send_command_prev(mock_orientation):
    ssh_mock = MagicMock()
    stdout_mock = MagicMock()
    stderr_mock = MagicMock()
    stdout_mock.read.return_value = b"output here"
    stderr_mock.read.return_value = b"errors here"
    ssh_mock.exec_command.return_value = (None, stdout_mock, stderr_mock)

    send_command.send_command(ssh_mock, "prev", "event2")

    expected_file = "/mnt/us/FlipCmd/prev_landscape.event"
    expected_command = f"cat {expected_file} > /dev/input/event2"
    ssh_mock.exec_command.assert_called_with(expected_command)
