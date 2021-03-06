import torch
from dataclasses import dataclass
from efficientnet_pytorch import EfficientNet
from torch.nn import CrossEntropyLoss
from transformers.file_utils import ModelOutput


@dataclass
class EfficientNetOutput(ModelOutput):
    loss: torch.FloatTensor = None
    logits: torch.FloatTensor = None
    features: torch.FloatTensor = None


class EfficientNetModify(EfficientNet):
    def __init__(self, blocks_args=None, global_params=None):
        super().__init__(blocks_args, global_params)

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
        if len(labels) > 0:
            loss_fun = CrossEntropyLoss()
            loss = loss_fun(logits, labels)

        return EfficientNetOutput(
            loss=loss,
            logits=logits,
            features=features
        )
