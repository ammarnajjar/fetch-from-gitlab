#!/usr/local/bin/python3.7
"""
Run all api services in parallel via dotnet run
"""

import glob
import json
import shlex
import subprocess
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


def main():
    configs = read_configs()
    apis = configs.get('apis')
    for api in apis:
        repo_path = path.join(path.dirname(path.realpath(__file__)), api)
        for project in glob.iglob(f'{repo_path}/**/*.csproj', recursive=True):
            if 'test' not in project.lower():
                title(api)
                job = Process(target=run, args=(project,))
                job.start()


if __name__ == '__main__':
    main()
