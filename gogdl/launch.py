import os
import json
import sys
import subprocess
import shlex

# Supports launching linux builds
def launch(arguments, unknown_args):
    print(arguments)
    info = load_game_info(arguments.path, arguments.id, arguments.platform)

    wrapper = []
    envvars = {}

    unified_platform = {
        'win32':'windows',
        'darwin':'osx',
        'linux':'linux'
    }

    if arguments.dont_use_wine == True or sys.platform == 'win32':
        wrapper_arg = arguments.wrapper
        wrapper = shlex.split(wrapper_arg)
    elif arguments.platform != unified_platform[sys.platform]:
        envvars['WINEPREFIX'] = arguments.wine_prefix
        wrapper = [arguments.wine]

    primary_task = get_primary_task(info)
    launch_arguments = primary_task.get('arguments')
    compatibility_flags = primary_task.get('compatibilityFlags')
    executable = os.path.join(arguments.path, primary_task['path'])
    if arguments.platform == 'linux':
        executable = os.path.join(arguments.path, 'game', primary_task['path'])
    if launch_arguments is None:
        launch_arguments = []
    if type(launch_arguments) == str:
        launch_arguments = shlex.split(launch_arguments)
    if compatibility_flags is None:
        compatibility_flags = []

    command = list()
    if len(wrapper) > 0 and wrapper[0] is not None:
        command.extend(wrapper)
    command.append(executable)
    command.extend(launch_arguments)
    command.extend(unknown_args)
    # command.append(compatibility_flags)
    
    working_dir = os.path.join(arguments.path, primary_task['workingDir'] if primary_task.get('workingDir') else '')

    enviroment = os.environ.copy()
    enviroment.update(envvars)
    process = subprocess.Popen(command, cwd=working_dir, env=enviroment)
    status = process.wait()
    sys.exit(status)

def get_primary_task(info):
    primaryTask = None
    for task in info['playTasks']:
        if task.get('isPrimary') == True:
            return task

def load_game_info(path, id, platform):
    filename = f'goggame-{id}.info'
    abs_path = (os.path.join(path, filename) if platform == "windows" else os.path.join(path, 'game', filename)) if platform != "osx" else os.path.join(path, 'Contents', 'Resources', filename)
    if not os.path.isfile(abs_path):
        sys.exit(1)
    with open(abs_path) as f:
        data = f.read()
        f.close()
        return json.loads(data)