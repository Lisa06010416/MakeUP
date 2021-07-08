import os
import torch
from dataclasses import dataclass
from efficientnet_pytorch import EfficientNet
from efficientnet_pytorch.utils import load_pretrained_weights
from torch.nn import CrossEntropyLoss
from transformers.file_utils import ModelOutput

from makeup.model.config_utils import Config
from  makeup.model.model_utils import BaseModel

def imageclassify_collect_fn(batch):
    data, labels = zip(*batch)
    data = torch.stack(data,0)
    return {"inputs":data, "labels":torch.tensor(labels)}

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
        # 原本的from_pretrained不會load fc layer
        model = cls.from_name(model_name, num_classes=num_classes, **override_params)
        model._change_in_channels(in_channels)
        weights_path = model._download_model_weight(weights_path)
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
