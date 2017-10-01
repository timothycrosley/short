"""Tests the Python3 implementation of shpaml3"""
import pytest

import short


def test_short():
    """Test to ensure short works as expected"""
    compiled = short.compile.text('> ,hey$there@is#something!more')
    assert 'class="hey"' in compiled
    assert 'name="there"' in compiled
    assert 'href="is"' in compiled
    assert 'id="something"' in compiled
    assert 'src="more"' in compiled

    assert short.compile.text(',here\n\tnor there') == '<div class="here">\n\tnor there\n</div>\n'
    assert short.compile.text('$here\n\tnor there') == '<div name="here">\n\tnor there\n</div>\n'
    assert short.compile.text('@here\n\tnor there') == '<div href="here">\n\tnor there\n</div>\n'
    assert short.compile.text('#here\n\tnor there') == '<div id="here">\n\tnor there\n</div>\n'
    assert short.compile.text('!here\n\tnor there') == '<div src="here">\n\tnor there\n</div>\n'

