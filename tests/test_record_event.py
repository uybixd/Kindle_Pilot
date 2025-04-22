import pytest
from unittest.mock import Mock, patch, call
from utils import record_event

@patch("utils.record_event.input", side_effect=[""])
@patch("utils.record_event.prompt_validation", side_effect=["yes"])
@patch("utils.record_event.time.sleep")
def test_record_single_command_success(mock_sleep, mock_prompt, mock_input):
    ssh = Mock()
    # 模拟 ssh.exec_command 的返回值
    channel_mock = Mock()
    channel_mock.recv_exit_status.return_value = 0
    ssh.exec_command.return_value = (None, Mock(channel=channel_mock), None)

    record_event.record_single_command(ssh, "测试下一页", "/mnt/us/FlipCmd/test_next.event", device="/dev/input/event1", duration=1)

    # 应该至少调用 mkdir 和 cat 两次（录制和验证）
    exec_calls = [call[0][0] for call in ssh.exec_command.call_args_list]
    assert any("mkdir -p" in cmd for cmd in exec_calls)
    assert any("cat /dev/input/event1 > /mnt/us/FlipCmd/test_next.event" in cmd for cmd in exec_calls)
    assert any("cat /mnt/us/FlipCmd/test_next.event > /dev/input/event1" in cmd for cmd in exec_calls)