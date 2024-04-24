import argparse
import os
import sys
from pathlib import Path
from typing import Final


class CommandArgs:
    config: Path | None = None
    analyze: bool = False


CMD_ARGS: Final = CommandArgs


def get_command_line_args(args=None) -> type[CommandArgs]:

    env_var_name = 'SML2MQTT_ANALYZE'

    parser = argparse.ArgumentParser(description='SML to MQTT bridge')
    parser.add_argument(
        '-c',
        '--config',
        help='Path to configuration file',
        default=None
    )
    parser.add_argument(
        '-a',
        '--analyze',
        help='Process exactly one sml message, shows the values of the message and what will be reported. '
             f'Can also be set by setting the environment variable "{env_var_name:s}" to an arbitrary value',
        action='store_true',
        default=False
    )
    args = parser.parse_args(args)
    CMD_ARGS.config = find_config_folder(args.config)
    CMD_ARGS.analyze = args.analyze or bool(os.environ.get(env_var_name, ''))

    return CMD_ARGS


def find_config_folder(config_file_str: str | None) -> Path:
    check_path = []

    if config_file_str is None:
        # Nothing is specified, we try to find the config automatically
        try:
            working_dir = Path.cwd()
            check_path.append(working_dir / 'sml2mqtt')
            check_path.append(working_dir.with_name('sml2mqtt'))
            check_path.append(working_dir.parent.with_name('sml2mqtt'))
        except ValueError:
            # the ValueError gets raised if the working_dir or its parent is empty (e.g. c:\ or /)
            pass

        check_path.append(Path.home() / 'sml2mqtt')   # User home

        # if we run in a venv check the venv, too
        if v_env := os.environ.get('VIRTUAL_ENV', ''):
            check_path.append(Path(v_env) / 'sml2mqtt')  # Virtual env dir

        for i, config_file in enumerate(check_path):
            check_path[i] = config_file = config_file.resolve() / 'config.yml'
            if config_file.is_file():
                return config_file
    else:
        config_file = Path(config_file_str).resolve()
        # Add to check_path, so we have a nice error message
        check_path.append(config_file)

        if config_file.is_file():
            return config_file

        # folder exists but not the file -> create file
        if config_file.parent.is_dir():
            return config_file

    # we have nothing found and nothing specified -> exit
    print('Config file not found!')
    print('Checked paths:\n - ' + '\n - '.join(str(k) for k in check_path))
    print('Please create file or specify a path with the "-c" arg switch.')
    sys.exit(1)
