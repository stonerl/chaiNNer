from __future__ import annotations

from spandrel import RestorationModelDescriptor, SRModelDescriptor
from spandrel.architectures.DAT import DAT
from spandrel.architectures.HAT import HAT
from spandrel.architectures.OmniSR import OmniSR
from spandrel.architectures.SCUNet import SCUNet
from spandrel.architectures.SRFormer import SRFormer
from spandrel.architectures.Swin2SR import Swin2SR
from spandrel.architectures.SwinIR import SwinIR

from nodes.impl.ncnn.model import NcnnModelWrapper
from nodes.properties.inputs import OnnxFpDropdown, SrModelInput
from nodes.properties.outputs import NcnnModelOutput, TextOutput

from .. import utility_group
from .convert_to_onnx import convert_to_onnx_node

try:
    from ....chaiNNer_onnx.onnx.utility.convert_to_ncnn import FP_MODE_32
    from ....chaiNNer_onnx.onnx.utility.convert_to_ncnn import (
        convert_to_ncnn_node as onnx_convert_to_ncnn_node,
    )
except Exception:
    onnx_convert_to_ncnn_node = None
    FP_MODE_32 = 0


@utility_group.register(
    schema_id="chainner:pytorch:convert_to_ncnn",
    name="Convert To NCNN",
    description=[
        "Convert a PyTorch model to NCNN. Internally, this node uses ONNX as an intermediate format, so the ONNX dependency must also be installed to use this node.",
        "It is recommended to save converted models as a separate step, then load the converted models instead of converting them every time you run the chain.",
        "Note: Converted models are not guaranteed to work with other programs that support NCNN models. This is for a variety of reasons and cannot be changed.",
    ],
    icon="NCNN",
    inputs=[
        SrModelInput("PyTorch Model"),
        OnnxFpDropdown(),
    ],
    outputs=[
        NcnnModelOutput(label="NCNN Model"),
        TextOutput("FP Mode", "FpMode::toString(Input1)"),
    ],
)
def convert_to_ncnn_node(
    model: SRModelDescriptor | RestorationModelDescriptor, is_fp16: int
) -> tuple[NcnnModelWrapper, str]:
    if onnx_convert_to_ncnn_node is None:
        raise ModuleNotFoundError(
            "Converting to NCNN is done through ONNX as an intermediate format (PyTorch -> ONNX -> NCNN), \
                and therefore requires the ONNX dependency to be installed. Please install ONNX through the dependency \
                manager to use this node."
        )

    assert not isinstance(
        model.model, (HAT, DAT, OmniSR, SwinIR, Swin2SR, SCUNet, SRFormer)
    ), f"{model.architecture} is not supported for NCNN conversions at this time."

    # Intermediate conversion to ONNX is always fp32
    onnx_model = convert_to_onnx_node(model, FP_MODE_32)[0]
    ncnn_model, fp_mode = onnx_convert_to_ncnn_node(onnx_model, is_fp16)

    return ncnn_model, fp_mode
