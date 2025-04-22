

import pytest
from unittest.mock import Mock
from utils import device_detector


def test_extract_event_device_success():
    input_text = """
I: Bus=0000 Vendor=0000 Product=0000 Version=0000
N: Name="pt_mt"
P: Phys=2-0024/input0
S: Sysfs=/devices/platform/input1
U: Uniq=
H: Handlers=event1 
B: PROP=2
B: EV=f
B: KEY=0
B: REL=0
B: ABS=2e18000 0

I: Bus=0019 Vendor=0001 Product=0001 Version=0100
N: Name="keyboard"
H: Handlers=event0
"""
    result = device_detector.extract_event_device(input_text)
    assert result == "event1"


def test_detect_touch_device_success():
    mock_ssh = Mock()
    mock_stdout = Mock()
    mock_stderr = Mock()

    mock_output = """
I: Bus=0000 Vendor=0000 Product=0000 Version=0000
N: Name="pt_mt"
P: Phys=2-0024/input0
S: Sysfs=/devices/platform/input1
U: Uniq=
H: Handlers=event3 
B: PROP=2
B: EV=f
B: KEY=0
B: REL=0
B: ABS=2e18000 0
"""
    mock_stdout.read.return_value = mock_output.encode()
    mock_stderr.read.return_value = b""
    mock_ssh.exec_command.return_value = (None, mock_stdout, mock_stderr)

    event = device_detector.detect_touch_device(mock_ssh)
    assert event == "event3"