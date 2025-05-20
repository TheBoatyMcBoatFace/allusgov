"""Tests for utility helpers."""

from allusgov.utils.utils import full_name


class FakeNode:
    """Minimal node implementation for testing ``full_name``."""

    def __init__(self, attrs=None):
        self._attrs = attrs or {}

    def get_attr(self, source_name):
        return self._attrs.get(source_name)

    def describe(self, exclude_prefix="_", exclude_attributes=None):
        for source, data in self._attrs.items():
            if exclude_attributes:
                data = {
                    k: v for k, v in data.items() if k not in exclude_attributes
                }
            yield source, data


def test_full_name_prefers_requested_source():
    node = FakeNode({"a": {"name": "Alpha"}, "b": {"name": "Beta"}})
    assert full_name(node, "b") == "Beta"


def test_full_name_falls_back_to_any_source():
    node = FakeNode({"a": {"name": "Alpha"}})
    assert full_name(node, "missing") == "Alpha"
