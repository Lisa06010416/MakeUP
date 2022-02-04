import os
import torch
from dataclasses import dataclass
from efficientnet_pytorch import EfficientNet
from efficientnet_pytorch.utils import url_map_advprop, url_map
from torch.nn import CrossEntropyLoss
from torch.utils import model_zoo
from transformers.file_utils import ModelOutput

from makeup.model.config_utils import Config
from makeup.model.model_utils import BaseModel
from makeup.utils.file_utils import MODELWEIGHTPATH2FILEIDL

def imageclassify_collect_fn(batch):
    data, labels = zip(*batch)
    data = torch.stack(data,0)
    return {"inputs":data, "labels":torch.tensor(labels)}


def load_pretrained_weights(model, model_name, weights_path=None, load_fc=True, advprop=False):
    """
    rewrite 原本 eficientnet 的 load_pretrained_weights function
    因為要在 torch.load 指定 device

    Loads pretrained weights from weights path or download using url.

    Args:
        model (Module): The whole model of efficientnet.
        model_name (str): Model name of efficientnet.
        weights_path (None or str):
            str: path to pretrained weights file on the local disk.
            None: use pretrained weights downloaded from the Internet.
        load_fc (bool): Whether to load pretrained weights for fc layer at the end of the model.
        advprop (bool): Whether to load pretrained weights
                        trained with advprop (valid when weights_path is None).
    """
    if isinstance(weights_path, str):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        state_dict = torch.load(weights_path, map_location= device)
    else:
        # AutoAugment or Advprop (different preprocessing)
        url_map_ = url_map_advprop if advprop else url_map
        state_dict = model_zoo.load_url(url_map_[model_name])

    if load_fc:
        ret = model.load_state_dict(state_dict, strict=False)
        assert not ret.missing_keys, 'Missing keys when loading pretrained weights: {}'.format(ret.missing_keys)
    else:
        state_dict.pop('_fc.weight')
        state_dict.pop('_fc.bias')
        ret = model.load_state_dict(state_dict, strict=False)
        assert set(ret.missing_keys) == set(['_fc.weight', '_fc.bias']), 'Missing keys when loading pretrained weights: {}'.format(ret.missing_keys)
    assert not ret.unexpected_keys, 'Missing keys when loading pretrained weights: {}'.format(ret.unexpected_keys)
    print('Loaded pretrained weights for {}'.format(model_name))


@dataclass
class EfficientNetOutput(ModelOutput):
    loss: torch.FloatTensor = None
    logits: torch.FloatTensor = None
    features: torch.FloatTensor = None


class EfficientNetModify(EfficientNet, BaseModel):
    def __init__(self, blocks_args=None, global_params=None):
        super().__init__(blocks_args, global_params)
        self.config = Config()
        for k,v in zip(global_params._fields, global_params):
            self.config.update_key_value(k, v)

    @classmethod
    def from_pretrained(cls, model_name, weights_path=None, advprop=False,
                        in_channels=3, num_classes=1000, load_fc=False, **override_params):
        """
        :param model_name:
        :param weights_path: list ["makeup_base_model"]
        :param advprop:
        :param in_channels:
        :param num_classes:
        :param load_fc:
        :param override_params:
        :return:
        """
        if model_name in MODELWEIGHTPATH2FILEIDL:
            num_classes = MODELWEIGHTPATH2FILEIDL[model_name].num_classes
            weights_path = cls._download_model_weight_from_googledrive(model_name)
            model_name = MODELWEIGHTPATH2FILEIDL[model_name].efficientnet_model_name
            load_fc = True
            include_top = False

        # 原本的from_pretrained不會load fc layer
        model = cls.from_name(model_name, num_classes=num_classes, **override_params)
        model._change_in_channels(in_channels)
        load_pretrained_weights(model, model_name, weights_path=weights_path, load_fc=load_fc,
                                advprop=advprop)
        # load config ! 測試
        if weights_path:
            dir_name, _ = os.path.split(weights_path)
            config_path = os.path.join(dir_name, "config.json")
            if os.path.isfile(config_path):
                model.config = Config.from_json_file(config_path)
        return model

    def forward(self,
                inputs=None,
                labels=None):
        features = super().forward(inputs)

        if self._global_params.include_top:
            logits = features
            features = None
        else:
            x = features.flatten(start_dim=1)
            x = self._dropout(x)
            logits = self._fc(x)
        loss = None
        if isinstance(labels, torch.Tensor):
            loss_fun = CrossEntropyLoss()
            loss = loss_fun(logits, labels)

        return EfficientNetOutput(
            loss=loss,
            logits=logits,
            features=features
        )
