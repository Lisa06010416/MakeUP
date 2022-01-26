import os
from google_drive_downloader import GoogleDriveDownloader as gdd

from makeup.utils.file_utils import MODELWEIGHTPATH2FILEIDL, SAVE_MODEL_PATH
from makeup.utils.logmanager import get_logger

logger = get_logger(__name__)

class BaseModel():
    @classmethod
    def _download_model_weight_from_googledrive(cls, model_name):
        save_path = SAVE_MODEL_PATH.format(model_name=model_name)
        if not os.path.isfile(save_path) and model_name in MODELWEIGHTPATH2FILEIDL:
            logger.info(f"download model {model_name} at {save_path}")
            gdd.download_file_from_google_drive(file_id=MODELWEIGHTPATH2FILEIDL[model_name].google_path,
                                                dest_path=save_path,
                                                unzip=False)
        return save_path
