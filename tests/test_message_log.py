"""Tests for the message log system."""

import pytest

from roguelike.ui.message_log import MessageLog


def test_message_log_initializes_empty():
    """Message log starts with no messages."""
    log = MessageLog()
    assert log.message_count == 0


def test_message_log_accepts_max_messages_parameter():
    """Message log respects max_messages parameter."""
    log = MessageLog(max_messages=50)
    assert log.max_messages == 50


def test_add_message_increases_count():
    """Adding a message increases message count."""
    log = MessageLog()
    log.add_message("Test message")
    assert log.message_count == 1


def test_add_message_stores_message():
    """Added message can be retrieved."""
    log = MessageLog()
    log.add_message("Test message")
    messages = log.get_messages()
    assert messages[0] == "Test message"


def test_add_empty_message_does_nothing():
    """Adding empty string does not add message."""
    log = MessageLog()
    log.add_message("")
    assert log.message_count == 0


def test_get_messages_returns_newest_first():
    """get_messages returns messages in reverse chronological order."""
    log = MessageLog()
    log.add_message("First")
    log.add_message("Second")
    log.add_message("Third")
    messages = log.get_messages()
    assert messages[0] == "Third"


def test_get_messages_with_count_limits_results():
    """get_messages with count parameter returns limited messages."""
    log = MessageLog()
    log.add_message("First")
    log.add_message("Second")
    log.add_message("Third")
    messages = log.get_messages(count=2)
    assert len(messages) == 2


def test_get_messages_with_count_returns_most_recent():
    """get_messages with count returns most recent messages."""
    log = MessageLog()
    log.add_message("First")
    log.add_message("Second")
    log.add_message("Third")
    messages = log.get_messages(count=2)
    assert messages[0] == "Third"


def test_message_log_enforces_max_messages():
    """Message log removes oldest messages when exceeding max."""
    log = MessageLog(max_messages=3)
    log.add_message("First")
    log.add_message("Second")
    log.add_message("Third")
    log.add_message("Fourth")
    assert log.message_count == 3


def test_message_log_keeps_newest_when_exceeding_max():
    """Oldest message is removed when exceeding max."""
    log = MessageLog(max_messages=3)
    log.add_message("First")
    log.add_message("Second")
    log.add_message("Third")
    log.add_message("Fourth")
    messages = log.get_messages()
    assert "First" not in messages


def test_clear_removes_all_messages():
    """clear method removes all messages."""
    log = MessageLog()
    log.add_message("First")
    log.add_message("Second")
    log.clear()
    assert log.message_count == 0


def test_get_messages_without_count_returns_all():
    """get_messages without count returns all messages."""
    log = MessageLog()
    log.add_message("First")
    log.add_message("Second")
    log.add_message("Third")
    messages = log.get_messages()
    assert len(messages) == 3
