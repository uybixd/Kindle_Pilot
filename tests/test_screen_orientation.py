import pytest
from unittest.mock import patch, MagicMock
from utils.screen_orientation import get_screen_orientation

def test_landscape_orientation():
    mock_ssh = MagicMock()
    mock_stdout = MagicMock()
    mock_stdout.read.return_value = b'mode "800x600"\n'
    mock_ssh.exec_command.return_value = (None, mock_stdout, None)
    assert get_screen_orientation(mock_ssh) == "landscape"

def test_portrait_orientation():
    mock_ssh = MagicMock()
    mock_stdout = MagicMock()
    mock_stdout.read.return_value = b'mode "600x800"\n'
    mock_ssh.exec_command.return_value = (None, mock_stdout, None)
    assert get_screen_orientation(mock_ssh) == "portrait"

def test_invalid_output():
    mock_ssh = MagicMock()
    mock_stdout = MagicMock()
    mock_stdout.read.return_value = b"abc"
    mock_ssh.exec_command.return_value = (None, mock_stdout, None)
    result = get_screen_orientation(mock_ssh)
    assert "Error" in result

def test_subprocess_error():
    mock_ssh = MagicMock()
    mock_ssh.exec_command.side_effect = Exception("cmd failed")
    result = get_screen_orientation(mock_ssh)
    assert "Error" in result