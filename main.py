#!/usr/local/bin/python3.7
"""
Clone/fetch projects from Gitlab using the private token
"""

import argparse
from os import path
import json
import subprocess
import shlex
from urllib.request import urlopen

IGNORE_LIST = [
    'test',
    'example',
    'tour'
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--token', '-t', help='Gitlab private Token')
    parser.add_argument('--url', '-u', help='Gitlab URL')
    args = parser.parse_args()

    if not args.token or not args.url:
        parser.print_help()
        exit(1)

    gitlab_token = args.token
    gitlab_url = args.url

    projects = urlopen(
        f'https://{gitlab_url}/api/v4/projects?membership=1&order_by=path&per_page=1000&private_token={gitlab_token}')
    all_projects = json.loads(projects.read().decode())

    for project in all_projects:
        try:
            url = project.get('ssh_url_to_repo')
            if any([x in url for x in IGNORE_LIST]):
                continue
            name = project.get('name').replace(' ', '-').replace('.', '-')
            repo_path = path.join(path.dirname(path.realpath(__file__)), name)
            if path.isdir(repo_path):
                print(f'Fetching {name}')
                command = shlex.split(f'git -C {repo_path} fetch')
                process = subprocess.Popen(command)
                process.communicate(input=None)
            else:
                print(f'Cloning {name}')
                command = shlex.split(f'git clone {url} {name}')
                process = subprocess.Popen(command)
                process.communicate(input=None)
        except Exception as unexpected_exception:
            print(f"Error on {url}: {str(unexpected_exception)}")
    print('Done')


if __name__ == '__main__':
    main()
