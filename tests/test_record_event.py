import pytest
from unittest.mock import Mock, patch
from utils import record_event

@patch('builtins.input', return_value='')
@patch('utils.record_event.prompt_yes_no', return_value=False)
def test_record_single_command(mock_prompt, mock_input):
    ssh_mock = Mock()
    ssh_mock.exec_command.return_value = (None, Mock(channel=Mock(recv_exit_status=Mock(return_value=0))), None)

    record_event.record_single_command(ssh_mock, "测试命令", "/mnt/us/FlipCmd/test.event")

    ssh_mock.exec_command.assert_any_call("mkdir -p /mnt/us/FlipCmd")
    assert any("cat" in call[0][0] for call in ssh_mock.exec_command.call_args_list)
