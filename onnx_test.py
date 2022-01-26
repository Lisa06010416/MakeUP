"""https://pytorch.org/tutorials/advanced/super_resolution_with_onnxruntime.html"""

import io
import numpy as np
from makeup import EfficientNetModify

from torch import nn
import torch.utils.model_zoo as model_zoo
import torch.onnx
import onnx
import onnxruntime


def to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()


class ConvertPytorch2Onnx:
    def _get_input(self, input_size):
        c, x, y = input_size
        batch_size = 1
        return torch.randn(batch_size, c, x, y, requires_grad=True)

    def convert(self, torch_model, input_size, onnx_save_path):
        torch_model.eval()

        input = self._get_input(input_size)

        torch.onnx.export(torch_model,  # model being run
                          input,  # model input (or a tuple for multiple inputs)
                          onnx_save_path,  # where to save the model (can be a file or file-like object)
                          export_params=True,  # store the trained parameter weights inside the model file
                          opset_version=10,  # the ONNX version to export the model to
                          do_constant_folding=True,  # whether to execute constant folding for optimization
                          input_names=['input'],  # the model's input names
                          output_names=['output'],  # the model's output names
                          dynamic_axes={'input': {0: 'batch_size'},  # variable length axes
                                        'output': {0: 'batch_size'}})

    def valid_onnx_model(self, pytorch_model, input_size, onnx_model_path, custom_to_numpy=None):
        self._check_schema(onnx_model_path)
        self._compare_to_pytorch_model(input_size, onnx_model_path, pytorch_model, custom_to_numpy)

    def _check_schema(self, onnx_model_path):
        onnx_model = onnx.load(onnx_model_path)
        # verify the model’s structure and confirm that the model has a valid schema
        onnx.checker.check_model(onnx_model)

    def _compare_to_pytorch_model(self, input_size, onnx_model_path, pytorch_model, custom_to_numpy=None):
        input = self._get_input(input_size)

        torch_out = pytorch_model(input)
        if custom_to_numpy:
            torch_out = custom_to_numpy(torch_out)
        else:
            torch_out = to_numpy(torch_out)

        ort_session = onnxruntime.InferenceSession(onnx_model_path)
        # ort_session.get_inputs()[0].name => input
        ort_inputs = {ort_session.get_inputs()[0].name: to_numpy(input)}
        ort_outs = ort_session.run(None, ort_inputs)

        # compare ONNX Runtime and PyTorch results
        if isinstance(torch_out, list):
            for data_i, data_j in zip(torch_out, ort_outs):
                np.testing.assert_allclose(data_i, data_j, rtol=1e-03, atol=1e-05)
        else:
            np.testing.assert_allclose(torch_out, ort_outs, rtol=1e-03, atol=1e-05)


def convert_efficient_net_model(effi_model_name, input_size, onnx_model_path):
    torch_model = EfficientNetModify.from_pretrained(effi_model_name,
                                                     num_classes=2,
                                                     include_top=False)
    torch_model.set_swish(memory_efficient=False)  # https://github.com/lukemelas/EfficientNet-PyTorch/issues/91

    # convert
    onnx_converter = ConvertPytorch2Onnx()
    onnx_converter.convert(torch_model, input_size, onnx_model_path)

    # valid
    def custom_to_numpy(model_output):
        return [to_numpy(model_output["logits"]), to_numpy(model_output["features"])]
    onnx_converter.valid_onnx_model(torch_model, input_size, onnx_model_path, custom_to_numpy)


if __name__ == "__main__":
    convert_efficient_net_model('efficientnet-b0', (3,224,224), "test.onnx")







