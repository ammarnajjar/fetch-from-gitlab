#!/usr/local/bin/python3.7
"""
Get all branches in the local workspace

The desired repos can be also provided through the argsv
by passing a part of the repo name
"""

import glob
import shlex
import subprocess
import sys
import time
from os import pardir, path

ROOT = path.dirname(path.abspath(__file__))


def timeit(callback):
    def wrapper(func):
        def inner(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            time_elapsed = end - start
            callback(f'Time needed = {time_elapsed:.2f} seconds.')
            return result
        return inner
    return wrapper


def print_green(text: str) -> None:
    print(f'\033[92m* {text}\033[0m')


def print_red(text: str) -> None:
    print(f'\033[91m* {text}\033[0m')


def print_yellow(text: str) -> None:
    print(f'\033[93m* {text}\033[0m')


def shell(command: str) -> str:
    cmd = shlex.split(command)
    output_lines = subprocess.check_output(cmd).decode("utf-8").split('\n')
    for index, line in enumerate(output_lines):
        if '*' in line:
            output_lines[index] = f'\033[93m{line}\033[0m'
    return '\n'.join(output_lines)


def hard_reset(repo_path) -> None:
    print_yellow(shell(f'git -C {repo_path} reset --hard'))


def get_branches(repo_path) -> None:
    print(shell(f'git -C {repo_path} branch -a'))


@timeit(print_yellow)
def main() -> None:
    reset_mode = False
    repos = []
    for repo in glob.iglob(f'{ROOT}/**/.git', recursive=True):
        repo_path = path.abspath(path.join(repo, pardir))
        repos.append(repo_path)

    args = sys.argv[1:]
    if 'reset' in args:
        del(args[args.index('reset')])
        reset_mode = True
        print_red('Reset mode enabled')

    if args:
        repos = list(filter(lambda repo: any(
            [arg in repo for arg in args]), [path.basename(repo) for repo in repos]))

    for repo_path in repos:
        print_green(repo_path)
        if reset_mode:
            hard_reset(repo_path)
        get_branches(repo_path)


if __name__ == '__main__':
    main()
