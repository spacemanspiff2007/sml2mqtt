import re

from easyconfig.yaml import yaml_rt

from sml2mqtt.config.config import Settings


def test_readme(pytestconfig) -> None:

    readme = pytestconfig.rootpath / 'readme.md'
    assert readme.is_file()

    yaml_parts = re.findall(r'```ya?ml\n(.+?)```', readme.read_text(encoding='utf-8'), re.DOTALL)

    # First entry is the complete config
    for cfg_sample in yaml_parts:
        obj = yaml_rt.load(cfg_sample)    # type: dict
        Settings(**obj)
