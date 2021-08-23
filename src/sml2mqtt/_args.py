import argparse
import os
import sys
import typing
from pathlib import Path


def find_config_folder(arg_config_path: typing.Optional[str]) -> Path:

    if arg_config_path is None:
        # Nothing is specified, we try to find the config automatically
        check_path = []
        try:
            working_dir = Path(os.getcwd())
            check_path.append(working_dir / 'sml2mqtt')
            check_path.append(working_dir.with_name('sml2mqtt'))
            check_path.append(working_dir.parent.with_name('sml2mqtt'))
        except ValueError:
            # the ValueError gets raised if the working_dir or its parent is empty (e.g. c:\ or /)
            pass

        check_path.append(Path.home() / 'sml2mqtt')   # User home

        # if we run in a venv check the venv, too
        v_env = os.environ.get('VIRTUAL_ENV', '')
        if v_env:
            check_path.append(Path(v_env) / 'sml2mqtt')  # Virtual env dir
    else:
        arg_config_path = Path(arg_config_path)

        # in case the user specifies the config.yml we automatically switch to the parent folder
        if arg_config_path.name.lower() == 'config.yml' and arg_config_path.is_file():
            arg_config_path = arg_config_path.parent

        # Override automatic config detection if something is specified through command line
        check_path = [arg_config_path]

    for config_folder in check_path:
        config_folder = config_folder.resolve()
        if not config_folder.is_dir():
            continue

        config_file = config_folder / 'config.yml'
        if config_file.is_file():
            return config_folder / 'config.yml'

    # we have specified a folder, but the config does not exist so we will create it
    if arg_config_path is not None and arg_config_path.is_dir():
        return arg_config_path / 'config.yml'

    # we have nothing found and nothing specified -> exit
    print('Config file "config.yml" not found!')
    print('Checked folders:\n - ' + '\n - '.join(str(k) for k in check_path))
    print('Please create file or specify a folder with the "-c" arg switch.')
    sys.exit(1)


class CommandArgs(typing.NamedTuple):
    config: typing.Optional[Path]
    analyze: bool


ARGS: CommandArgs


def get_command_line_args(args=None) -> CommandArgs:
    global ARGS

    parser = argparse.ArgumentParser(description='SML to MQTT bridge')
    parser.add_argument(
        '-c',
        '--config',
        help='Path to configuration folder',
        default=None
    )
    parser.add_argument(
        '-a',
        '--analyze',
        help='Processes exactly one sml message and explicitly shows the structure',
        action='store_true',
        default=False
    )
    args = parser.parse_args(args)
    ARGS = CommandArgs(config=find_config_folder(args.config), analyze=args.analyze)
    return ARGS
