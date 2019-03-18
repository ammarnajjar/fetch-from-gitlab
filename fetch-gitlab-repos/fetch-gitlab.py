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
from collections import defaultdict
from os import path
from urllib.request import urlopen

ROOT = path.dirname(path.abspath(__file__))


def read_configs():
    configs = {}
    try:
        with open(f'{ROOT}/config.json', 'r') as config_file:
            configs = json.loads(config_file.read())
    except FileNotFoundError:
        print('config.json cannot be found')
    except json.decoder.JSONDecodeError:
        print('Please provide gitlab configs in json format')
    return configs


def print_green(text):
    print(f'\033[92m* {text}\033[0m')


def print_red(text):
    print(f'\033[93m* {text}\033[0m')


def shell(command):
    cmd = shlex.split(command)
    return subprocess.check_output(cmd).decode("utf-8").split('\n')[0]


def main():
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

    summery_info = defaultdict()
    for project in all_projects:
        url = project.get('ssh_url_to_repo')
        name = project.get('name').replace(' ', '-').replace('.', '-')
        repo_path = path.join(path.dirname(path.realpath(__file__)), name)
        if path.isdir(repo_path):
            print_green(f'Fetching {name}')
            shell(f'git -C {repo_path} fetch')
            remote_banches = shell(f'git -C {repo_path} ls-remote --heads')
            current_branch = shell(
                f'git -C {repo_path} rev-parse --abbrev-ref HEAD --')
            summery_info.update({name: current_branch})
            if (f'refs/heads/{current_branch}' in remote_banches):
                shell(
                    f'git -C {repo_path} fetch -u origin {current_branch}:{current_branch}')
            else:
                print_red(f'{current_branch} does not exist on remote')

            if ('refs/heads/develop' in remote_banches and current_branch != 'develop'):
                shell(f'git -C {repo_path} fetch origin develop:develop')
        else:
            print_green(f'Cloning {name}')
            shell(f'git clone {url} {name}')

    print('==============')
    print_green('Repos Summery:')
    for repo_name, current_branch in summery_info.items():
        print_red(f'{repo_name} => {current_branch}')

    sys.exit(0)


if __name__ == '__main__':
    main()
