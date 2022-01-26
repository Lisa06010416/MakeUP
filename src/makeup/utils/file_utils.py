import os

from collections import namedtuple

ModelInfo = namedtuple("ModelInfo", "google_path, efficientnet_model_name, num_classes")
MODELWEIGHTPATH2FILEIDL = {
"makeup_base_model" : ModelInfo(google_path="1XEsZMKtUHyBsKceH0pIoraglUVgnKhJg",
                                efficientnet_model_name="efficientnet-b4",
                                num_classes=4)
}


CATCH_PATH = os.path.join(os.path.expanduser('~') ,".cache")
SAVE_MODEL_PATH = os.path.join(CATCH_PATH, "makeup/{model_name}/pytorch_model.bin")
