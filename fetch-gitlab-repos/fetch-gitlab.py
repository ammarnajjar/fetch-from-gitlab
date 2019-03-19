#!/usr/local/bin/python3.7
"""
Clone/fetch projects from Gitlab using the private token

The desired repos can be also provided through the argsv
by passing a part of the repo name

NOTE:
The gitlab url, token should be provided in a config.json
file, which should exist in the same direcotry as this script.
"""

import json
import shlex
import subprocess
import sys
import time
from collections import defaultdict
from multiprocessing import Manager, Pool
from os import path
from typing import Dict
from urllib.request import urlopen

ROOT = path.dirname(path.abspath(__file__))


def read_configs() -> Dict[str, str]:
    configs = {}
    try:
        with open(f'{ROOT}/config.json', 'r') as config_file:
            configs = json.loads(config_file.read())
    except FileNotFoundError:
        print('config.json cannot be found')
    except json.decoder.JSONDecodeError:
        print('Please provide gitlab configs in json format')
    return configs


def print_green(text: str) -> None:
    print(f'\033[92m* {text}\033[0m')


def print_yellow(text: str) -> None:
    print(f'\033[93m* {text}\033[0m')


def shell(command: str) -> str:
    cmd = shlex.split(command)
    return subprocess.check_output(cmd).decode("utf-8").split('\n')[0]


def fetch_repo(name: str, summery_info: Dict[str, str]) -> None:
    repo_path = path.join(path.dirname(path.realpath(__file__)), name)
    if path.isdir(repo_path):
        print_green(f'Fetching {name}')
        shell(f'git -C {repo_path} fetch')
        remote_banches = shell(f'git -C {repo_path} ls-remote --heads')
        current_branch = shell(
            f'git -C {repo_path} rev-parse --abbrev-ref HEAD --')
        if (f'refs/heads/{current_branch}' in remote_banches):
            shell(
                f'git -C {repo_path} fetch -u origin {current_branch}:{current_branch}')
        else:
            print_yellow(f'{current_branch} does not exist on remote')

        if ('refs/heads/develop' in remote_banches and current_branch != 'develop'):
            shell(f'git -C {repo_path} fetch origin develop:develop')
    else:
        print_green(f'Cloning {name}')
        shell(f'git clone {url} {name}')
        current_branch = shell(
            f'git -C {repo_path} rev-parse --abbrev-ref HEAD --')
    summery_info.update({name: current_branch})


def main() -> None:
    start = time.time()
    configs = read_configs()
    gitlab_url = configs.get('gitlab_url')
    gitlab_token = configs.get('gitlab_token')
    if not(gitlab_url and gitlab_token):
        print('Please provide gitlab configs in your config.json')
        sys.exit(1)

    projects = urlopen(
        f'https://{gitlab_url}/api/v4/projects?membership=1&order_by=path&per_page=1000&private_token={gitlab_token}')
    all_projects = json.loads(projects.read().decode())

    args = sys.argv[1:]
    if args:
        all_projects = list(filter(lambda pro: any(
            [arg in pro.get('name') for arg in args]),
            [project for project in all_projects]))

    ignore_list = configs.get('ignore_list')
    if ignore_list:
        all_projects = list(filter(lambda pro: all(
            [ignored_repo not in pro.get('name') for ignored_repo in ignore_list]),
            [project for project in all_projects]))

    manager = Manager()
    summery_info = manager.dict()

    pool = Pool(processes=8)
    for project in all_projects:
        url = project.get('ssh_url_to_repo')
        name = project.get('name').replace(' ', '-').replace('.', '-')
        pool.apply_async(fetch_repo, args=(name, summery_info))
    pool.close()
    pool.join()

    end = time.time()
    print('==============')
    print_green(f'Summery: (fetched in {(end - start):.2f} seconds)')
    for repo_name, current_branch in summery_info.items():
        print_yellow(f'{repo_name} => {current_branch}')


if __name__ == '__main__':
    main()
