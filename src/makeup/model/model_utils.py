import os
from google_drive_downloader import GoogleDriveDownloader as gdd

from makeup.utils.file_utils import MODELWEIGHTPATH2FILEIDL, CATCH_PATH

class BaseModel():
    def _download_model_weight(self, model_name):
        save_path = CATCH_PATH.format(model_name=model_name)
        if not os.path.isfile(save_path) and model_name in MODELWEIGHTPATH2FILEIDL.keys():
            gdd.download_file_from_google_drive(file_id=MODELWEIGHTPATH2FILEIDL[model_name],
                                                dest_path=save_path,
                                                unzip=False)
        return save_path