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


import os
import sys
import time
from signal import SIG_DFL
from signal import SIGPIPE
from signal import signal

import click
import sh

signal(SIGPIPE, SIG_DFL)
from getpass import getpass
from pathlib import Path
from typing import ByteString
from typing import Generator
from typing import Iterable
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

#from with_sshfs import sshfs
#from with_chdir import chdir
from asserttool import nevd
from asserttool import pause
from asserttool import root_user
from enumerate_input import enumerate_input
from pathtool import comment_out_line_in_file
from replace_text import append_unique_bytes_to_file
#from pathtool import write_line_to_file
from retry_on_exception import retry_on_exception


def eprint(*args, **kwargs):
    if 'file' in kwargs.keys():
        kwargs.pop('file')
    print(*args, file=sys.stderr, **kwargs)


try:
    from icecream import ic  # https://github.com/gruns/icecream
    from icecream import icr  # https://github.com/jakeogh/icecream
except ImportError:
    ic = eprint
    icr = eprint


def validate_slice(slice_syntax):
    assert isinstance(slice_syntax, str)
    for c in slice_syntax:
        if c not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', '[', ']', ':']:
            raise ValueError(slice_syntax)
    return slice_syntax


def add_host_to_ssh_config(hostname: str,
                           user: str,
                           verbose: bool,
                           debug: bool,
                           ):

    config_section = "\n\nHost {hostname}\n\tPubkeyAuthentication yes\n\tUser {user}\n\tIdentityFile ~/.ssh/id_rsa__%r@%h\n".format(hostname=hostname, user=user,)
    if verbose:
        ic(hostname, user, config_section)
    #write_line_to_file(path='~/.ssh/config', unique=True, line=line, verbose=verbose, debug=debug,)
    append_unique_bytes_to_file(path='~/.ssh/config',
                                bytes_to_append=config_section.encode('utf8'),
                                verbose=verbose,
                                debug=debug,)


def generate_ssh_key_files(user: str,
                           hostname: str,
                           key_size: int,
                           no_password: bool,
                           exist_ok: bool,
                           verbose: bool,
                           debug: bool,
                           ) -> Path:

    id_rsa_file = Path('~/.ssh/id_rsa__{user}@{hostname}'.format(user=user, hostname=hostname)).expanduser()
    if id_rsa_file.exists():
        if not exist_ok:
            raise FileExistsError(id_rsa_file)

        eprint(id_rsa_file.as_posix(), 'exists, skiping key generation')
        return id_rsa_file

    keygen_command = sh.ssh_keygen.bake('-vvv', '-t', 'rsa', '-b', key_size, '-C', '', '-f', id_rsa_file.as_posix())
    if not no_password:     # using a password
        password = getpass('Enter passphrase (empty for no passphrase): ')
    else:
        password = ''

    keygen_command.bake('-N', password)

    eprint('\nGenerating {key_size}bit RSA key'.format(key_size=key_size))
    keygen_command()

    assert id_rsa_file.exists()
    return id_rsa_file


@click.group()
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.pass_context
def cli(ctx,
        verbose: bool,
        debug: bool,
        ):

    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['debug'] = debug


@cli.command()
@click.argument("user", type=str, nargs=1)
@click.argument("hostname", type=str, nargs=1)
@click.option('--key-size', type=int, default=16384,)
@click.option('--no-password', is_flag=True)
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.pass_context
def generate_and_install_key(ctx,
                             user: str,
                             key_size: int,
                             no_password: bool,
                             hostname: str,
                             verbose: bool,
                             debug: bool,
                             ):

    if root_user():
        pause("\nAre you sure you want to do this as root?\n")

    ctx.ensure_object(dict)
    null, end, verbose, debug = nevd(ctx=ctx,
                                     printn=False,
                                     ipython=False,
                                     verbose=verbose,
                                     debug=debug,)

    id_rsa_file = generate_ssh_key_files(key_size=key_size,
                                         user=user,
                                         hostname=hostname,
                                         no_password=no_password,
                                         exist_ok=True,
                                         verbose=verbose,
                                         debug=debug,)
    if verbose:
        ic(id_rsa_file)

    add_host_to_ssh_config(hostname=hostname,
                           user=user,
                           verbose=verbose,
                           debug=debug,)

    public_keyfile = Path(id_rsa_file.as_posix() + '.pub')
    if verbose:
        ic(public_keyfile)
    #sh.ssh_copy_id('-i', public_keyfile.as_posix(), user + '@' + hostname)
    ssh_copy_id_command = ' '.join(['ssh-copy-id', '-i', public_keyfile.as_posix(), user + '@' + hostname])
    if verbose:
        ic(ssh_copy_id_command)
    os.system(ssh_copy_id_command)



@cli.command()
@click.argument("hostname", type=str, nargs=1)
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.pass_context
def forget_known_host(ctx,
                      hostname: str,
                      verbose: bool,
                      debug: bool,
                      ):

    if root_user():
        pause("\nAre you sure you want to do this as root?\n")

    ctx.ensure_object(dict)
    null, end, verbose, debug = nevd(ctx=ctx,
                                     printn=False,
                                     ipython=False,
                                     verbose=verbose,
                                     debug=debug,)

    known_hosts = Path('~/.ssh/known_hosts').expanduser().resolve()
    if verbose:
        ic(known_hosts)
    assert known_hosts.exists()
    comment_out_line_in_file(path=known_hosts,
                             line_to_match=hostname + " ",
                             startswith=True,
                             verbose=verbose,
                             debug=debug)
