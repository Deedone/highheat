import json
import os
from pathlib import Path
from bbclient import BBClient

from highheat.log import logger

CURRENT_VERSION = 1
#TODO: Figure out how to do this less badly

class ProjectData:
    sourcedir: Path
    imagedir: Path | None
    deploydir: Path | None
    workdir: Path
    recpie_path: Path
    srcrev: str
    recipes: list[str]
    version: int
    
    def __init__(self, sourcedir: str, imagedir: str | None, deploydir: str | None, workdir: str, recpie_path: str, srcrev: str = "", recipes: list[str] = [], version: int = CURRENT_VERSION):
        self.sourcedir = Path(sourcedir)
        self.imagedir = None
        if imagedir is not None and imagedir != "None":
            self.imagedir = Path(imagedir)
        self.deploydir = None
        if deploydir is not None and deploydir != "None":
            self.deploydir = Path(deploydir)
        self.workdir = Path(workdir)
        self.recpie_path = Path(recpie_path)
        self.srcrev = srcrev
        self.recipes = recipes
    
    def to_json(self):
        return {
            'sourcedir': str(self.sourcedir),
            'imagedir': str(self.imagedir),
            'deploydir': str(self.deploydir),
            'workdir': str(self.workdir),
            'recpie_path': str(self.recpie_path),
            'srcrev': self.srcrev,
            'recipes': json.dumps(self.recipes)
        }
    
    @classmethod
    def from_json(cls, data: dict):
        return cls(
            data['sourcedir'],
            data['imagedir'],
            data['deploydir'],
            data['workdir'],
            data['recpie_path'],
            data['srcrev'],
            json.loads(data['recipes'])
        )
        
class BBdata:
    data: dict[str, ProjectData]
    saved_path: Path
    
    def __init__(self, yoctobuilddir: Path):
        self.saved_path = yoctobuilddir / '.hh_data.json'
        self.data = {}
        try:
            if self.saved_path.exists():
                with open(self.saved_path, 'r') as f:
                    logger.debug("Loading data from %s", self.saved_path)
                    json_data = json.load(f)
                    if 'version' not in json_data or json_data['version'] != str(CURRENT_VERSION):
                        logger.warning("Data version mismatch, reinitializing")
                        return
                    for key, value in json_data.items():
                        if key == 'version':
                            continue
                        self.data[key] = ProjectData.from_json(value)
        except json.JSONDecodeError:
            logger.warning("Failed to load data from %s, reinitializing", self.saved_path)
            
            
    def save(self):
        logger.debug("Saving data to %s", self.saved_path)
        with open(self.saved_path, 'w') as f:
            json_data:dict[str, dict|str] = {key: value.to_json() for key, value in self.data.items()}
            json_data['version'] = str(CURRENT_VERSION)
            json.dump(json_data, f, default=vars)

    def append(self, key: str, value: ProjectData):
        self.data[key] = value
        self.save()
        
    def check_entry(self, key:str) -> bool:
        logger.debug("Checking entry %s", key)
        if key not in self.data:
            return False
            
        if not self.data[key].sourcedir.exists():
            return False
        imagedir = self.data[key].imagedir
        if imagedir is not None:
            if not imagedir.exists():
                return False
        
        deploydir = self.data[key].deploydir
        if deploydir is not None:
            if not deploydir.exists():
                return False
        if not self.data[key].workdir.exists():
            return False
        if not self.data[key].recpie_path.exists():
            return False
        
        return True

    def bb_load_projectdata(self, yocto_root: Path, builddir: Path, project: str) -> bool:
        logger.debug("yocto root: %s", yocto_root)
        
        poky_path = yocto_root / "poky"
        if not poky_path.exists():
            logger.error("poky not found at %s", poky_path)
            return False
    
        relative_builddir = builddir.relative_to(yocto_root)
        logger.debug("relative builddir: %s", relative_builddir)
        logger.info("Launching BBClient to get project data for %s", project)
        logger.debug("bbclient = BBClient( %s %s %s", str(poky_path), "source oe-init-build-env ../"+str(relative_builddir), ")")
        bbclient = BBClient(str(poky_path), "source oe-init-build-env ../"+str(relative_builddir))
        # Settings to prevent BB server from destroying workdirs that it deems obsolete
        os.environ.update({"SSTATE_PRUNE_OBSOLETEWORKDIR": "0", "BB_ENV_PASSTHROUGH_ADDITIONS": "SSTATE_PRUNE_OBSOLETEWORKDIR"})
        logger.debug("OS environment variables: %s", os.environ)
        bbclient.start_server()
        
        recipe = bbclient.find_best_provider(project)[-1]
        logger.info("Loading variables for %s", recipe)
        idx = bbclient.parse_recipe_file(recipe)
        if idx is None:
            logger.error("Failed to parse %s", recipe)
            bbclient.stop_server()
            return False
            
        sourcedir = bbclient.data_store_connector_cmd(idx, "getVar", "S")
        imagedir = bbclient.data_store_connector_cmd(idx, "getVar", "D")
        deploydir = bbclient.data_store_connector_cmd(idx, "getVar", "DEPLOYDIR")
        workdir = bbclient.data_store_connector_cmd(idx, "getVar", "WORKDIR")
        srcrev = bbclient.data_store_connector_cmd(idx, "getVar", "SRCREV")
        recipes = [recipe]
        for append in bbclient.get_file_appends(recipe):
            recipes.append(append)
        
        bbclient.stop_server()
        logger.debug("Loaded S:%s \nI:%s \nD:%s \nW:%s\nR:%s\n from %s", sourcedir, imagedir, deploydir, workdir, recipes, recipe)
        
        if not sourcedir:
            logger.error("sourcedir not found")
            return False
        if not imagedir:
            logger.warning("imagedir not found")
        if not deploydir:
            logger.warning("deploydir not found")
        if not workdir:
            logger.error("workdir not found")
            return False
        
        proj_data = ProjectData(sourcedir, imagedir, deploydir, workdir, recipe, srcrev, recipes)
        
        self.append(project, proj_data)
        return True
