from efficientnet_pytorch import EfficientNet

class clasify_efficientnet(EfficientNet):
    def __init__(self, config):
        super().__init__()
        self.classify_num = config.classify_num

    def forward(self):
        pass

