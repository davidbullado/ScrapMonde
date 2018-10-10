import sys

def printerr(f_arg, *argv, **kwargs):
    print('\033[91m', f_arg, argv, kwargs, '\033[0m', file=sys.stderr)