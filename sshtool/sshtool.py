#!/usr/bin/env python3
# -*- coding: utf8 -*-

# flake8: noqa           # flake8 has no per file settings :(
# pylint: disable=C0111  # docstrings are always outdated and wrong
# pylint: disable=C0114  #      Missing module docstring (missing-module-docstring)
# pylint: disable=W0511  # todo is encouraged
# pylint: disable=C0301  # line too long
# pylint: disable=R0902  # too many instance attributes
# pylint: disable=C0302  # too many lines in module
# pylint: disable=C0103  # single letter var names, func name too descriptive
# pylint: disable=R0911  # too many return statements
# pylint: disable=R0912  # too many branches
# pylint: disable=R0915  # too many statements
# pylint: disable=R0913  # too many arguments
# pylint: disable=R1702  # too many nested blocks
# pylint: disable=R0914  # too many local variables
# pylint: disable=R0903  # too few public methods
# pylint: disable=E1101  # no member for base
# pylint: disable=W0201  # attribute defined outside __init__
# pylint: disable=R0916  # Too many boolean expressions in if statement
# pylint: disable=C0305  # Trailing newlines editor should fix automatically, pointless warning

# code style:
#   no guessing on spelling: never tmp_X always temporary_X
#   no guessing on case: local vars, functions and methods are lower case. classes are ThisClass(). Globals are THIS.
#   del vars explicitely ASAP, assumptions are buggy
#   rely on the compiler, code verbosity and explicitness can only be overruled by benchamrks (are really compiler bugs)
#   no tabs. code must display the same independent of viewer
#   no recursion, recursion is undecidiable, randomly bounded, and hard to reason about
#   each elementis the same, no special cases for the first or last elemetnt:
#       [1, 2, 3,] not [1, 2, 3]
#       def this(*.
#                a: bool,
#                b: bool,
#               ):
#
#   expicit loop control is better than while (condition):
#       while True:
#           # continue/break explicit logic


# TODO:
#   https://github.com/kvesteri/validators
import os
import sys
import click
import time
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)
from pathlib import Path
#from with_sshfs import sshfs
#from with_chdir import chdir
from asserttool import nevd
from retry_on_exception import retry_on_exception
from enumerate_input import enumerate_input
#from collections import defaultdict
#from prettyprinter import cpprint, install_extras
#install_extras(['attrs'])

#from kcl.configops import click_read_config
#from kcl.configops import click_write_config_entry

#from kcl.userops import not_root
#from pathtool import path_is_block_special
#from getdents import files
#from prettytable import PrettyTable
#output_table = PrettyTable()

from typing import List
from typing import Tuple
from typing import Sequence
from typing import Generator
from typing import Iterable
from typing import ByteString
from typing import Optional

# click-command-tree
#from click_plugins import with_plugins
#from pkg_resources import iter_entry_points

def eprint(*args, **kwargs):
    if 'file' in kwargs.keys():
        kwargs.pop('file')
    print(*args, file=sys.stderr, **kwargs)


try:
    from icecream import ic  # https://github.com/gruns/icecream
    from icecream import icr # https://github.com/jakeogh/icecream
except ImportError:
    ic = eprint
    icr = eprint


# import pdb; pdb.set_trace()
# #set_trace(term_size=(80, 24))
# from pudb import set_trace; set_trace(paused=False)

##def log_uncaught_exceptions(ex_cls, ex, tb):
##   eprint(''.join(traceback.format_tb(tb)))
##   eprint('{0}: {1}'.format(ex_cls, ex))
##
##sys.excepthook = log_uncaught_exceptions

def get_timestamp():
    timestamp = str("%.22f" % time.time())
    return timestamp


def validate_slice(slice_syntax):
    assert isinstance(slice_syntax, str)
    for c in slice_syntax:
        if c not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', '[', ']', ':']:
            raise ValueError(slice_syntax)
    return slice_syntax


#@with_plugins(iter_entry_points('click_command_tree'))
#@click.group()
#@click.option('--verbose', is_flag=True)
#@click.option('--debug', is_flag=True)
#@click.pass_context
#def cli(ctx,
#        verbose: bool,
#        debug: bool,
#        ):
#
#    ctx.ensure_object(dict)
#    ctx.obj['verbose'] = verbose
#    ctx.obj['debug'] = debug




# DONT CHANGE FUNC NAME
@click.command()
@click.argument("paths", type=str, nargs=-1)
@click.argument("sysskel",
                type=click.Path(exists=False,
                                dir_okay=True,
                                file_okay=False,
                                path_type=str,
                                allow_dash=False,),
                nargs=1,
                required=True,)
@click.argument("slice_syntax", type=validate_slice, nargs=1)
#@click.option('--add', is_flag=True)
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.option('--simulate', is_flag=True)
@click.option('--ipython', is_flag=True)
@click.option('--count', is_flag=True)
@click.option('--skip', type=int, default=False)
@click.option('--head', type=int, default=False)
@click.option('--tail', type=int, default=False)
@click.option("--printn", is_flag=True)
#@click.option("--progress", is_flag=True)
@click.pass_context
def cli(ctx,
        paths,
        sysskel: str,
        slice_syntax: str,
        verbose: bool,
        debug: bool,
        simulate: bool,
        ipython: bool,
        count: bool,
        skip: int,
        head: int,
        tail: int,
        printn: bool,
        ):

    ctx.ensure_object(dict)
    null, end, verbose, debug = nevd(ctx=ctx,
                                     printn=printn,
                                     ipython=False,
                                     verbose=verbose,
                                     debug=debug,)

    #progress = False
    #if (verbose or debug):
    #    progress = False

    #ctx.obj['end'] = end
    #ctx.obj['null'] = null
    #ctx.obj['progress'] = progress
    ctx.obj['count'] = count
    ctx.obj['skip'] = skip
    ctx.obj['head'] = head
    ctx.obj['tail'] = tail

    #global APP_NAME
    #config, config_mtime = click_read_config(click_instance=click,
    #                                         app_name=APP_NAME,
    #                                         verbose=verbose,
    #                                         debug=debug,)
    #if verbose:
    #    ic(config, config_mtime)

    #if add:
    #    section = "test_section"
    #    key = "test_key"
    #    value = "test_value"
    #    config, config_mtime = click_write_config_entry(click_instance=click,
    #                                                    app_name=APP_NAME,
    #                                                    section=section,
    #                                                    key=key,
    #                                                    value=value,
    #                                                    verbose=verbose,
    #                                                    debug=debug,)
    #    if verbose:
    #        ic(config)

    iterator = paths

    index = 0
    for index, path in enumerate_input(iterator=iterator,
                                       dont_decode=True,  # paths are bytes
                                       null=null,
                                       progress=False,
                                       skip=skip,
                                       head=head,
                                       tail=tail,
                                       debug=debug,
                                       verbose=verbose,):
        path = Path(os.fsdecode(path))

        if verbose:  # or simulate:
            ic(index, path)
        #if count:
        #    if count > (index + 1):
        #        ic(count)
        #        sys.exit(0)

        #if simulate:
        #    continue

        with open(path, 'rb') as fh:
            path_bytes_data = fh.read()

        if not count:
            print(path, end=end)

    if count:
        print(index + 1, end=end)

#        if ipython:
#            import IPython; IPython.embed()

#@cli.command()
#@click.argument("urls", type=str, nargs=-1)
#@click.option('--verbose', is_flag=True)
#@click.option('--debug', is_flag=True)
#@click.pass_context
#def some_command(ctx,
#                 urls,
#                 verbose: bool,
#                 debug: bool,
#                 ):
#    if verbose:
#        ctx.obj['verbose'] = verbose
#    verbose = ctx.obj['verbose']
#    if debug:
#        ctx.obj['debug'] = debug
#    debug = ctx.obj['debug']
#
#    iterator = urls
#    for index, url in enumerate_input(iterator=iterator,
#                                      null=ctx.obj['null'],
#                                      progress=ctx.obj['progress'],
#                                      skip=ctx.obj['skip'],
#                                      head=ctx.obj['head'],
#                                      tail=ctx.obj['tail'],
#                                      debug=ctx.obj['debug'],
#                                      verbose=ctx.obj['verbose'],):
#
#        if ctx.obj['verbose']:
#            ic(index, url)


