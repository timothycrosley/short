""" short

    A simple pre-processing template language that produces valid html / xml from condensed input

    re-release of public domain software created by Steve Howell

    Copyright (C) 2017  Timothy Edmund Crosley

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
    documentation files (the "Software"), to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
    to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or
    substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
    TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
    CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.
"""
import re

MAGIC_ATTRIBUTES = {'#': 'id', '@': 'href', '$': 'name', ',': 'class', '!': 'src', '*': 'accessor'}
STRAIGHT_MAGIC = ''.join(MAGIC_ATTRIBUTES.keys())
ESCAPED_MAGIC = ''.join(re.escape(magic) for magic in MAGIC_ATTRIBUTES.keys())
QUOTED__text = r"""(?:(?:'(?:\\'|[^'])*')|(?:"(?:\\"|[^"])*"))"""
PASS_SYNTAX = 'PASS'
FLUSH_LEFT_SYNTAX = '|| '
FLUSH_LEFT_EMPTY_LINE = '||'
TAG_WHITESPACE_ATTRS = re.compile('(\S+)([ \t]*?)(.*)')
TAG_AND_REST = re.compile(r'((?:[^ \t{}]|\.\.)+)(.*)'.format(ESCAPED_MAGIC))
ATTRIBUTES = re.compile(r'([{}])((?:[^ \t{}]|\.\.)+)'.format(STRAIGHT_MAGIC, ESCAPED_MAGIC))
COMMENT_SYNTAX = re.compile(r'^::comment$')
VERBATIM_SYNTAX = re.compile('(.+) VERBATIM$')
DIV_SHORTCUT = re.compile(r'^(?:[{0}](?!\.))'.format(ESCAPED_MAGIC))
AUTO_QUOTE = re.compile("""([ \t]+[^ \t=]+=)(""" + QUOTED__text + """|[^ \t]+)""")

def _auto_quote_attributes(attrs):
    def _sub(m):
        attr = m.group(2)
        if attr[0] in "\"'":
            return m.group(1) + attr
        return m.group(1) + '"' + attr + '"'
    return re.sub(AUTO_QUOTE, _sub, attrs)


def syntax(regex):
    def wrap(function):
        function.regex = re.compile(regex)
        return function
    return wrap


@syntax('([ \t]*)(.*)')
def _indent(m):
    prefix, line = m.groups()
    line = line.rstrip()
    if line == '':
        prefix = ''
    return prefix, line


@syntax('^([%<{]\S.*)')
def _raw_html(m):
    return m.group(1).rstrip()


@syntax('^\| (.*)')
def _text(m):
    return m.group(1).rstrip()


@syntax('(.*?) > (.*)')
def _outer_closing_tag(m):
    tag, text = m.groups()
    text = convert_line(text)
    return enclose_tag(tag, text)


@syntax('(.*?) \| (.*)')
def _text_enclosing_tag(m):
    tag, text = m.groups()
    return enclose_tag(tag, text)


@syntax('> (.*)')
def self_closing_tag(m):
    tag = m.group(1).strip()
    if tag and tag[0] in STRAIGHT_MAGIC:
        tag = "div{}".format(tag)
    return '<%s />' % apply_magic(tag)[0]


@syntax('>< (.*)')
def empty_tag(m):
    tag = m.group(1).strip()
    if tag and tag[0] in STRAIGHT_MAGIC:
        tag = "div{}".format(tag)
    return '<{}></{}>'.format(*apply_magic(tag))


@syntax('(.*)')
def _raw_text(m):
    return m.group(1).rstrip()


line_methods = (_raw_html, _text, _outer_closing_tag, _text_enclosing_tag, self_closing_tag, empty_tag, _raw_text)


def text(short):
    """Compiles short markup text into an HTML strings"""
    return indent(short, branch_method=html_block_tag, leaf_method=convert_line, pass_syntax=PASS_SYNTAX,
                  flush_left_syntax=FLUSH_LEFT_SYNTAX, flush_left_empty_line=FLUSH_LEFT_EMPTY_LINE,
                  indentation_method=find_indentation)


def html_block_tag(output, block, recurse):
    append = output.append
    prefix, tag = block[0]
    if _raw_html.regex.match(tag):
        append(prefix + tag)
        recurse(block[1:])
    elif COMMENT_SYNTAX.match(tag):
        pass
    elif VERBATIM_SYNTAX.match(tag):
        m = VERBATIM_SYNTAX.match(tag)
        tag = m.group(1).rstrip()
        start_tag, end_tag = apply_magic_sugar(tag)
        append(prefix + start_tag)
        stream(append, block[1:])
        append(prefix + end_tag)
    else:
        start_tag, end_tag = apply_magic_sugar(tag)
        append(prefix + start_tag)
        recurse(block[1:])
        append(prefix + end_tag)


def stream(append, prefix_lines):
    for prefix, line in prefix_lines:
        if line == '':
            append('')
        else:
            append(prefix + line)


def convert_line(line):
    prefix, line = find_indentation(line.strip())
    for method in line_methods:
        m = method.regex.match(line)
        if m:
            return prefix + method(m)


def apply_magic_sugar(markup):
    if DIV_SHORTCUT.match(markup):
        markup = 'div' + markup
    start_tag, tag = apply_magic(markup)
    return ('<%s>' % start_tag, '</%s>' % tag)


def apply_magic(markup):
    tag, whitespace, attrs = TAG_WHITESPACE_ATTRS.match(markup).groups()
    tag, rest = tag_and_rest(tag)
    attrs = _auto_quote_attributes(attrs)
    for attribute, value in magic_attributes(rest).items():
        attrs += ' {}="{}"'.format(attribute, value)
    start_tag = tag + whitespace + attrs
    return start_tag, tag


def magic_attributes(rest):
    attributes = {}
    if not rest:
        return attributes

    ATTRIBUTES.sub(lambda match: attributes.setdefault(MAGIC_ATTRIBUTES.get(match.group(1),
                                                                            'class'), []).append(match.group(2)), rest)
    return {name: fixdots(' '.join(value)) for name, value in attributes.items()}


def fixdots(text):
    return text.replace('..', '.')


def tag_and_rest(tag):
    match = TAG_AND_REST.match(tag)
    if not match:
        return fixdots(tag), None
    return fixdots(match.group(1)), match.group(2)


def enclose_tag(tag, text):
    start_tag, end_tag = apply_magic_sugar(tag)
    return start_tag + text + end_tag


def find_indentation(line):
    """Returns a pair of basestrings.

    The first consists of leading spaces and tabs in line. The second
    is the remainder of the line with any trailing space stripped off.

    Parameters
    ----------

      line : basestring
    """
    return _indent(_indent.regex.match(line))


def get_indented_block(prefix_lines):
    """Returns an integer.

    The return value is the number of lines that belong to block begun
    on the first line.

    Parameters
    ----------

      prefix_lines : list of basestring pairs
        Each pair corresponds to a line of SHPAML source code. The
        first element of each pair is indentation. The second is the
        remaining part of the line, except for trailing newline.
    """
    prefix, line = prefix_lines[0]
    len_prefix = len(prefix)

    # Find the first nonempty line with len(prefix) <= len(prefix)
    i = 1
    while i < len(prefix_lines):
        new_prefix, line = prefix_lines[i]
        if line and len(new_prefix) <= len_prefix:
            break
        i += 1

    # Rewind to exclude empty lines
    while i - 1 > 0 and prefix_lines[i - 1][1] == '':
        i -= 1

    return i


def indent(text, branch_method, leaf_method, pass_syntax, flush_left_syntax, flush_left_empty_line, indentation_method,
           get_block=get_indented_block):
    """Returns HTML as a basestring.

    Parameters
    ----------

      text : basestring
        Source code, typically SHPAML, but could be a different (but
        related) language. The remaining parameters specify details
        about the language used in the source code. To parse SHPAML,
        pass the same values as convert_shpaml_tree.

      branch_method : function
        convert_shpaml_tree passes html_block_tag here.
      leaf_method : function
        convert_shpaml_tree passes convert_line here.

      pass_syntax : basestring
        convert_shpaml_tree passes PASS_SYNTAX here.
      flush_left_syntax : basestring
        convert_shpaml_tree passes FLUSH_LEFT_SYNTAX here.
      flush_left_empty_line : basestring
        convert_shpaml_tree passes FLUSH_LEFT_EMPTY_LINE here.

      indentation_method : function
        convert_shpaml_tree passes _indent here.

      get_block : function
        Defaults to get_indented_block.
    """
    text = text.rstrip()
    lines = text.split('\n')
    if lines and lines[0].startswith('!! '):
        lines[0] = lines[0].replace('!! ', '<!DOCTYPE ') + '>'
    output = []
    indent_lines(lines, output, branch_method, leaf_method, pass_syntax, flush_left_syntax, flush_left_empty_line,
                 indentation_method, get_block=get_indented_block)
    return '\n'.join(output) + '\n'


def indent_lines(lines, output, branch_method, leaf_method, pass_syntax, flush_left_syntax, flush_left_empty_line,
                 indentation_method, get_block):
    """Returns None.

    The way this function produces output is by adding strings to the
    list that's passed in as the second parameter.

    Parameters
    ----------

      lines : list of basestring's
        Each string is a line of a SHPAML source code
        (trailing newlines not included).
      output : empty list
        Explained earlier...

    The remaining parameters are exactly the same as in the indent
    function:

      * branch_method
      * leaf_method
      * pass_syntax
      * flush_left_syntax
      * flush_left_empty_line
      * indentation_method
      * get_block
    """
    append = output.append

    def recurse(prefix_lines):
        while prefix_lines:
            prefix, line = prefix_lines[0]
            if line == '':
                prefix_lines.pop(0)
                append('')
                continue

            block_size = get_block(prefix_lines)
            if block_size == 1:
                prefix_lines.pop(0)
                if line == pass_syntax:
                    pass
                elif line.startswith(flush_left_syntax):
                    append(line[len(flush_left_syntax):])
                elif line.startswith(flush_left_empty_line):
                    append('')
                else:
                    append(prefix + leaf_method(line))
            else:
                block = prefix_lines[:block_size]
                prefix_lines = prefix_lines[block_size:]
                branch_method(output, block, recurse)
        return
    prefix_lines = list(map(indentation_method, lines))
    recurse(prefix_lines)
