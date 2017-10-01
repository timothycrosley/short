"""Tests the Python3 implementation of shpaml3"""
import pytest

import short


def test_short():
    """Test to ensure short works as expected"""
    compiled = short.compile.text('> .hey$there@is#something')
    assert 'class="hey"' in compiled
    assert 'name="there"' in compiled
    assert 'href="is"' in compiled
    assert 'id="something"' in compiled

