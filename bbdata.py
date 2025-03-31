import json
from pathlib import Path
from bbclient import BBClient
from log import logger


class ProjectData:
    sourcedir: Path
    imagedir: Path
    deploydir: Path
    workdir: Path
    recpie_path: Path
    
    def __init__(self, sourcedir: str, imagedir: str, deploydir: str, workdir: str, recpie_path: str):
        self.sourcedir = Path(sourcedir)
        self.imagedir = None
        if imagedir is not None and imagedir != "None":
            self.imagedir = Path(imagedir)
        self.deploydir = None
        if deploydir is not None and deploydir != "None":
            self.deploydir = Path(deploydir)
        self.workdir = Path(workdir)
        self.recpie_path = Path(recpie_path)
    
    def to_json(self):
        return {
            'sourcedir': str(self.sourcedir),
            'imagedir': str(self.imagedir),
            'deploydir': str(self.deploydir),
            'workdir': str(self.workdir),
            'recpie_path': str(self.recpie_path)
        }
    
    @classmethod
    def from_json(cls, data: dict):
        return cls(
            data['sourcedir'],
            data['imagedir'],
            data['deploydir'],
            data['workdir'],
            data['recpie_path']
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
                    for key, value in json_data.items():
                        self.data[key] = ProjectData.from_json(value)
                    
                    
                    return
        except json.JSONDecodeError:
            logger.warn("Failed to load data from %s, reinitializing", self.saved_path)
            
            
    def save(self):
        logger.debug("Saving data to %s", self.saved_path)
        with open(self.saved_path, 'w') as f:
            json_data = {key: value.to_json() for key, value in self.data.items()}
            json.dump(json_data, f, default=vars)

    def append(self, key: str, value: ProjectData):
        self.data[key] = value
        self.save()
        
    def check_entry(self, key:str) -> bool:
        if key not in self.data:
            return False
            
        if not self.data[key].sourcedir.exists():
            return False
        if not self.data[key].imagedir.exists():
            return False
        if not self.data[key].deploydir.exists():
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
        bbclient.stop_server()
        logger.debug("Loaded S:%s \nI:%s \nD:%s \nW:%s\n from %s", sourcedir, imagedir, deploydir, workdir, recipe)
        
        if not sourcedir:
            logger.error("sourcedir not found")
            return False
        if not imagedir:
            logger.error("imagedir not found")
            return False
        if not deploydir:
            logger.error("deploydir not found")
            return False
        if not workdir:
            logger.error("workdir not found")
            return False
        
        proj_data = ProjectData(sourcedir, imagedir, deploydir, workdir, recipe)
        
        self.append(project, proj_data)
        return True
