#!/usr/local/bin/python3.7
"""
Run all api services in parallel via dotnet run

It also accepts command line arguments to filter
the projects desired to start
"""

import glob
import json
import shlex
import subprocess
import sys
from multiprocessing import Process
from os import path

ROOT = path.dirname(path.abspath(__file__))


def title(text):
    print(f'\033[92m* {text}\033[0m')


def run(project):
    command = shlex.split(f'dotnet run -p {project}')
    process = subprocess.Popen(command)
    process.communicate(input=None)


def read_configs():
    configs = {}
    try:
        with open(f'{ROOT}/config.json', 'r') as config_file:
            configs = json.loads(config_file.read())
    except FileNotFoundError:
        print('config.json cannot be found')
    return configs


def start_service(service_name):
    repo_path = path.join(path.dirname(path.realpath(__file__)), service_name)
    for project in glob.iglob(f'{repo_path}/**/*.csproj', recursive=True):
        if 'test' not in project.lower():
            title(service_name)
            job = Process(target=run, args=(project,))
            job.start()


def main():
    configs = read_configs()
    apis = configs.get('apis')
    args = sys.argv[1:]

    if len(args) > 0:
        apis = list(filter(lambda x: any([arg in x for arg in args]), apis))
    for api in apis:
        start_service(api)


if __name__ == '__main__':
    main()
