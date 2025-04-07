from pathlib import Path
from typing import Dict
import yaml

from highheat.log import logger


def find_yaml_path() -> Path|None:
    start = Path.cwd()
    # Check if current directory has *.yaml and build.ninja

    while start != Path('/'):
        if list(start.glob('*.yaml')) and Path.exists(start / 'build.ninja'):
            yamls = list(start.glob('*.yaml'))
            return yamls[0]
        start = start.parent

# Layout
# components:
#   dom0:
#     build-dir: "%{YOCTOS_WORK_DIR}"
#     builder:
#       type: yocto
#       work_dir: "%{DOM0_BUILD_DIR}"
#   domd:
#     build-dir: "%{YOCTOS_WORK_DIR}"
#   domu:
#     build-dir: "%{YOCTOS_WORK_DIR}"

#TODO: Check in moulin if this is okay
def process_variables(path: Path, yaml_data) -> Path:

    variables = yaml_data['variables']
    if not variables:
        return path

    strpath = str(path)
    for variable in variables:
        if variable in strpath:
            strpath = strpath.replace("%{"+variable+"}", variables[variable])

    return Path(strpath)

def get_build_dirs(yaml_path: Path) -> Dict[str, Path]:
    paths:Dict[str, Path] = {}
    basedir = yaml_path.parent

    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)

    if 'components' not in data:
        logger.error("components not found in %s", yaml_path)
        return {}

    components = data['components']
    for component in components:
        if 'build-dir' in components[component] and 'builder' in components[component] and 'work_dir' in components[component]['builder']:
            build_dir = basedir / components[component]['build-dir'] / components[component]['builder']['work_dir']
            build_dir = process_variables(build_dir, data)
            paths[component] = build_dir
    return paths
