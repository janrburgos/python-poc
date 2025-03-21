# tests/test_tasks.py

import datetime
from app.tasks import sample_task, say_something


def test_sample_task_adds_correctly():
    result = sample_task.apply(args=(1, 2, 3)).get()
    assert result == 5


def test_say_something_prints_message(mocker, capsys):
    fake_time = datetime.datetime(2025, 3, 21, 12, 0, 0)

    # Mock datetime.datetime.now using mocker
    mock_datetime = mocker.patch("app.tasks.datetime")
    mock_datetime.datetime.now.return_value = fake_time

    say_something.apply(args=["Test message"])
    captured = capsys.readouterr()

    assert "2025-03-21 12:00:00 Test message" in captured.out


def test_say_something_prints_default_message(mocker, capsys):
    fake_time = datetime.datetime(2025, 3, 21, 12, 0, 0)

    # Mock datetime.datetime.now using mocker
    mock_datetime = mocker.patch("app.tasks.datetime")
    mock_datetime.datetime.now.return_value = fake_time

    say_something.apply()
    captured = capsys.readouterr()

    assert "2025-03-21 12:00:00 Hello" in captured.out
