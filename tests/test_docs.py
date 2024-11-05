from collections.abc import Callable
from dataclasses import dataclass
from inspect import getmembers, isclass
from pathlib import Path
from typing import Any

from _pytest.monkeypatch import derive_importpath
from easyconfig import yaml
from pydantic import BaseModel

import sml2mqtt
from sml2mqtt.config.inputs import SmlSourceSettingsBase
from sml2mqtt.config.operations import HasDateTimeFields, HasIntervalFields
from sml2mqtt.sml_value.setup_operations import MAPPING, setup_operations


@dataclass
class YamlBlock:
    file: Path
    line_no: int
    model: str
    lines: list[str]

    def validate(self, func: Callable[[BaseModel],Any] | None = None):
        sample_cfg = '\n'.join(self.lines)

        target, name = derive_importpath(self.model, True)
        model_cls = getattr(name, target)   # type: type[BaseModel]

        try:
            yaml_obj = yaml.yaml_rt.load(sample_cfg)
            model = model_cls.model_validate(yaml_obj)
            if func:
                func(model)
        except Exception:
            print('')
            print(f'Error in {self.file.parent.name}/{self.file.name}:{self.line_no}')
            raise


def validate_yaml_blocks(file: Path, prefix_model: str = 'yamlmodel: ', func: Callable[[BaseModel],Any] | None = None):

    current_module = ''

    model = ''
    obj: YamlBlock | None = None
    indentation = 0

    for line_no, line in enumerate(file.read_text().splitlines()):
        line = line
        line_low = line.strip().lower()

        if line_low.startswith('.. py:currentmodule::'):
            current_module = line.strip()[21:].strip()

        if line_low.startswith(prefix_model):
            assert not model
            model = line.strip()[len(prefix_model):]
            if '.' not in model:
                if not current_module:
                    msg = f'currentmodule not set in {file}:{line_no}'
                    raise ValueError(msg)
                model = f'{current_module}.{model}'

        if obj is not None:
            # we need one empty line before the yaml starts
            if not obj.lines and line_low:
                continue

            # find out indentation
            if not indentation and line_low:
                while line[indentation] == ' ':
                    indentation += 1

            # we have a non-indented line -> yaml is finished
            if line_low and line[0] != ' ':
                obj.validate(func)
                obj = None
                indentation = 0
                model = ''
                continue

            obj.lines.append(line)

        if line_low.startswith(('.. code-block:: yaml', '.. code-block:: yml')):
            if not model:
                msg = f'Model object not set in {file}:{line_no}'
                raise ValueError(msg)
            if obj is not None:
                msg = f'Object already set in {file}:{line_no}: {obj.model} line {obj.line_no}'
                raise ValueError(msg)

            obj = YamlBlock(file, line_no, model, [])

    if obj:
        obj.validate(func)


def test_yaml_samples(pytestconfig) -> None:

    class DummyOperationParent:
        def add_operation(self, obj) -> None:
            pass

    class HasOperationsModel(BaseModel):
        operations: list[BaseModel]

    def check_obj(model: BaseModel) -> None:
        if model.__class__ in MAPPING:
            setup_operations(DummyOperationParent(), HasOperationsModel(operations=[model]))

    for file in (pytestconfig.rootpath / 'docs').iterdir():
        if file.suffix.lower() == '.rst':
            validate_yaml_blocks(file, func=check_obj)


def _get_documented_objs(path: Path, objs: set[str]) -> None:

    current_module = ''

    for line in (x.strip().replace('  ', '') for x in path.read_text().splitlines()):  # type: str
        if line.startswith('.. py:currentmodule::'):
            current_module = line[21:].strip()
            continue

        if line.startswith('.. autopydantic_model::'):
            obj_name = line[23:].strip()
            if '.' not in obj_name:
                assert current_module
                obj_name = f'{current_module}.{obj_name}'
            assert obj_name not in objs
            objs.add(obj_name)


def test_config_documentation_complete(pytestconfig) -> None:
    cfg_model_dir: Path = pytestconfig.rootpath / 'src' / 'sml2mqtt' / 'config'
    assert cfg_model_dir.is_dir()

    documented_objs = set()
    _get_documented_objs(pytestconfig.rootpath / 'docs' / 'configuration.rst', documented_objs)
    _get_documented_objs(pytestconfig.rootpath / 'docs' / 'operations.rst', documented_objs)

    # get Config implementation from source
    existing_objs = set()
    for module_name in [f.stem for f in cfg_model_dir.glob('**/*.py')]:
        module = getattr(sml2mqtt.config, module_name)
        cfg_objs = [
            x[1] for x in getmembers(
                module, lambda x: isclass(x) and issubclass(x, BaseModel) and x not in (
                    SmlSourceSettingsBase, HasIntervalFields, HasDateTimeFields
                )
            )
        ]
        cfg_names = {
            f'{obj.__module__}.{obj.__qualname__}' for obj in cfg_objs if not obj.__module__.startswith('easyconfig.')
        }
        existing_objs.update(cfg_names)

        # we check this here to get the module with the error message
        missing = cfg_names - documented_objs
        assert not missing, module.__name__

    # ensure that everything that is implemented is documented
    assert existing_objs == documented_objs
