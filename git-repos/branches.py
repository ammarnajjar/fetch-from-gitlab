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


def print_yellow(text: str) -> None:
    print(f'\033[93m* {text}\033[0m')


def shell(command: str) -> str:
    cmd = shlex.split(command)
    output_lines = subprocess.check_output(cmd).decode("utf-8").split('\n')
    for index, line in enumerate(output_lines):
        if '*' in line:
            output_lines[index] = f'\033[93m{line}\033[0m'
    return '\n'.join(output_lines)


def get_branches(repo_path) -> str:
    return shell(f'git -C {repo_path} branch -a')


@timeit(print_yellow)
def main() -> None:
    repos = []
    for repo in glob.iglob(f'{ROOT}/**/.git', recursive=True):
        repo_path = path.abspath(path.join(repo, pardir))
        repos.append(repo_path)

    args = sys.argv[1:]
    if args:
        repos = list(filter(lambda repo: any(
            [arg in repo for arg in args]), [path.basename(repo) for repo in repos]))

    for repo_path in repos:
        print_green(repo_path)
        print(get_branches(repo_path))


if __name__ == '__main__':
    main()
