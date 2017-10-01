import os
import sys

import hug

from short._version import current
from short.compile import text

INTRO = """
 /##########################################################\

         __   ; `.'  :
        |  +. :  ;   :   __
      .-+\\   `:  ;   ,,-'  :                SHORT
      `.  `.  `\\ ;  :'   ,'
     ,-+`+. `. \\.;.:  _,' `-.        Grow up your markup
     `.__  "-.::||::.:'___-+'
     -"  `--..::::::_____.IIHb
    `-:______.:; `::,,...,;:HB\\
     .+         \\ ::,,...,;:HB \\
    '-.______.:+ \\`+.,...,;:P'  \\
    .-'           \\              \\
    `-.______.:+   \\______________\\
    .-::::::::,     BBBBBBBBBBBBBBB       Version {}
    ::,,...,;:HB    BBBBBBBBBBBBBBB
    ::,,...,;:HB    BBBBBBBBBBBBBBB   Copyright (C) 2017
    ::,,...,;:HB\\   BBBBBBBBBBBBBBB
    ::,,...,;:HB \\  BBBBBBBBBBBBBBB  Timothy Edmund Crosley
    `+.,...,;:P'  \\ BBBBBBBBBBBBBBB
                   \\BBBBBBBBBBBBBBB   Under the MIT License

 \\##########################################################/

""".format(current)


def iter_source_code(paths, in_ext="py"):
    """Iterate over all Python source files defined in paths."""
    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    if filename.endswith('.' + in_ext):
                        yield os.path.join(dirpath, filename).lstrip('./')
        else:
            yield path


@hug.cli(version=current)
def grow(files: hug.types.multiple, in_ext: hug.types.text="short", out_ext: hug.types.text="html",
         out_dir: hug.types.text="", recursive: hug.types.smart_boolean=False):
    """Grow up your markup"""
    if files == ['-']:
        print(text(sys.stdin.read()))
        return

    print(INTRO)
    if recursive:
        files = iter_source_code(files, in_ext)

    for file_name in files:
        with open(file_name, 'r') as input_file:
            output_file_name = "{0}.{1}".format(os.path.join(out_dir, ".".join(file_name.split('.')[:-1])), out_ext)
            with open(output_file_name, 'w') as output_file:
                print("   |-> [{2}]: {3} '{0}' -> '{1}' till it's not short...".format(file_name, output_file_name,
                                                                                       'HTML', 'Growing'))
                output_file.write(text(input_file.read()))

    print("   |")
    print("   |                 >>> Done Growing! :) <<<")
    print("")


