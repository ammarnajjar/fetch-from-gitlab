#!/usr/local/bin/python3.7
"""
Clone/fetch projects from Gitlab using the private token

NOTE:
The gitlab url, token should be provided in a config.json
file, which should exist in the same direcotry as this script.
"""

import json
import shlex
import subprocess
import sys
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
    ignore_list = configs.get('ignore_list')

    projects = urlopen(
        f'https://{gitlab_url}/api/v4/projects?membership=1&order_by=path&per_page=1000&private_token={gitlab_token}')
    all_projects = json.loads(projects.read().decode())

    for project in all_projects:
        try:
            url = project.get('ssh_url_to_repo')
            if any([x in url for x in ignore_list]):
                continue
            name = project.get('name').replace(' ', '-').replace('.', '-')
            repo_path = path.join(path.dirname(path.realpath(__file__)), name)
            if path.isdir(repo_path):
                print(f'Fetching {name}')
                shell(f'git -C {repo_path} fetch')
                current_branch = shell(
                    f'git -C {repo_path} rev-parse --abbrev-ref HEAD --')
                shell(
                    f'git -C {repo_path} fetch -u origin {current_branch}:{current_branch}')
                if (current_branch != 'develop'):
                    shell(f'git -C {repo_path} fetch origin develop:develop')
            else:
                print(f'Cloning {name}')
                shell(f'git clone {url} {name}')
        except Exception as unexpected_exception:
            print(f"Error on {url}: {str(unexpected_exception)}")
    print('Done')
    sys.exit(0)


if __name__ == '__main__':
    main()
