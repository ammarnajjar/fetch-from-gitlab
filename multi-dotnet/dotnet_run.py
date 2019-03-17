#!/usr/local/bin/python3.7
"""
Run all dotnet services in parallel via dotnet run

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


def print_green(text):
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
            print_green(service_name)
            job = Process(target=run, args=(project,))
            job.start()


def main():
    configs = read_configs()
    dotnet_projects = configs.get('dotnet_projects')

    args = sys.argv[1:]
    if args:
        dotnet_projects = list(filter(lambda pro: any(
            [arg in pro for arg in args]), dotnet_projects))

    for dotnet_project in dotnet_projects:
        start_service(dotnet_project)


if __name__ == '__main__':
    main()
