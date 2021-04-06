import torch

from torchvision import datasets, transforms
from transformers import Trainer, TrainingArguments

from src.lisa.model.metrics import acc_metrics
from src.lisa.model.efficientnet import EfficientNetModify, imageclassify_collect_fn


class TestEfficientNetModify:
    model_name = 'efficientnet-b4'

    def test_get_model(self):
        model = EfficientNetModify.from_pretrained(self.model_name, num_classes=4, include_top=False)
        assert isinstance(model, EfficientNetModify)

    def test_predict(self):
        image_size = 224
        valid_data_path = "testdata/img/valid"
        model_name = 'efficientnet-b0'

        valid_data = datasets.ImageFolder(valid_data_path,
                                             transforms.Compose([
                                                 transforms.Resize(image_size),
                                                 transforms.CenterCrop(image_size),
                                                 transforms.RandomAffine(degrees=0, translate=(0.05, 0.05)),
                                                 transforms.RandomHorizontalFlip(),
                                                 transforms.ToTensor(),
                                                 transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                                                      std=[0.229, 0.224, 0.225]),
                                             ]))
        valid_dataloader = torch.utils.data.DataLoader(valid_data,
                                                       batch_size=2,
                                                       shuffle=True,
                                                       num_workers=1)


        model = EfficientNetModify.from_pretrained(model_name,
                                                   num_classes=2,
                                                   include_top=False)

        for data in valid_dataloader:
            model.eval()
            images, labels = data
            outputs = model(images, labels)
            assert outputs["logits"].size() == torch.Size([2, 2])
            assert outputs["features"].size() == torch.Size([2, 1280, 1, 1])
            assert isinstance(outputs["loss"].item(), float)

    def test_train_with_trainer(self):
        image_size = 224
        train_data_path = "testdata/img/train"
        valid_data_path = "testdata/img/valid"
        model_name = 'efficientnet-b0'
        output_dir = "./results"
        train_dataset = datasets.ImageFolder(train_data_path,
                                             transforms.Compose([
                                                 transforms.Resize(image_size),
                                                 transforms.CenterCrop(image_size),
                                                 transforms.RandomAffine(degrees=0, translate=(0.05, 0.05)),
                                                 transforms.RandomHorizontalFlip(),
                                                 transforms.ToTensor(),
                                                 transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                                                      std=[0.229, 0.224, 0.225]),
                                             ]))
        valid_dataset = datasets.ImageFolder(valid_data_path,
                                             transforms.Compose([
                                                 transforms.Resize(image_size),
                                                 transforms.CenterCrop(image_size),
                                                 transforms.RandomAffine(degrees=0, translate=(0.05, 0.05)),
                                                 transforms.RandomHorizontalFlip(),
                                                 transforms.ToTensor(),
                                                 transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                                                      std=[0.229, 0.224, 0.225]),
                                             ]))
        model = EfficientNetModify.from_pretrained(model_name, num_classes=2, include_top=False)

        training_args = TrainingArguments(
            output_dir=output_dir,  # 輸出模型的資料夾
            # num_train_epochs=2,  # 訓練代數
            max_steps=3,
            per_device_train_batch_size=2,  # train時的batch size
            per_device_eval_batch_size=2,  # eval時的batch size
            gradient_accumulation_steps=1,  # 每幾個batch update一次參數
            # load_best_model_at_end=True,  # 訓練完後自動讀取最佳的model, trainer 會忽略 save_strategy,save_steps 在每次eval後存模型
            warmup_steps=500,  # 前幾個batch要做warm up
            weight_decay=0.00001,  # learning rate decay
            eval_steps=50,  # 每幾個step要eval 預設500
            save_steps=1,            # 每幾個step要save 預設500
            logging_steps=1,
            evaluation_strategy="steps",  # 用STEPS來判斷是否要eval
            dataloader_num_workers=2,  # 開幾個CPU做dataloader
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=valid_dataset,
            data_collator=imageclassify_collect_fn,
            compute_metrics=acc_metrics
        )

        # save config
        model.config.update_key_value("classes", train_dataset.classes)
        model.config.save_pretrained(output_dir)

        trainer.train()


        predict = trainer.predict(valid_dataset)
        print(predict.predictions[1].shape)
        assert predict.predictions[0].shape == (4, 2)
        assert predict.predictions[1].shape == (4, 1280, 1, 1)
        assert isinstance(predict.metrics["eval_accuracy"], float)
