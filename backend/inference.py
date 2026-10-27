"""Shared preprocessing and logit interpretation for serving and evaluation."""
import math

import numpy as np
from PIL import Image, ImageOps


def infer_image(image, runner):
    input_spec = runner.get_input_details()[0]
    output_spec = runner.get_output_details()[0]
    _, height, width, channels = input_spec['shape']
    if channels != 3 or input_spec['dtype'] != np.float32:
        raise ValueError('Unsupported model input')
    image = ImageOps.exif_transpose(image).convert('RGB')
    pixels = np.asarray(image.resize((int(width), int(height)), Image.Resampling.BILINEAR), dtype=np.float32)
    runner.set_tensor(input_spec['index'], np.expand_dims(pixels / 127.5 - 1.0, 0))
    runner.invoke()
    score = float(runner.get_tensor(output_spec['index']).reshape(-1)[0])
    if not math.isfinite(score):
        raise ValueError('Non-finite output')
    probability = 1 / (1 + math.exp(-max(-80, min(80, score))))
    return score, probability
