import os
from typing import Callable, List, Dict

import numpy as np
import onnxruntime as ort
from src.texts import text_to_sequence

class BaseClassOnnxInfer:
    @staticmethod
    def create_onnx_infer(
        infer_factor: Callable,
        onnx_model_path: str,
        providers: List[str],
        session_options: ort.SessionOptions = None,
        onnx_params: Dict = None,
    ):
        if not os.path.exists(onnx_model_path):
            raise FileNotFoundError(f"ONNX model not found: {onnx_model_path}")

        session = ort.InferenceSession(
            path_or_bytes=onnx_model_path,
            providers=providers,
            sess_options=BaseClassOnnxInfer.adjust_onnx_session_options(session_options),
            **(onnx_params or {}),
        )

        fn = infer_factor(session)
        fn.__session = session
        return fn

    @staticmethod
    def get_def_onnx_session_options():
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        return session_options

    @staticmethod
    def adjust_onnx_session_options(session_options: ort.SessionOptions = None):
        return session_options or BaseClassOnnxInfer.get_def_onnx_session_options()


class TTS(BaseClassOnnxInfer):
    
    PreferredProviders = ["CPUExecutionProvider", "CUDAExecutionProvider"]

    def __init__(
        self,
        onnx_model_path: str,
        execution_provider: str = None,
        verbose: bool = False,
        onnx_session_options: ort.SessionOptions = None,
        onnx_params: Dict = None,
    ):

        if verbose:
            print("Loading configuration...")

        # Normalize execution provider name
        if execution_provider and not execution_provider.endswith("ExecutionProvider"):
            execution_provider = f"{execution_provider}ExecutionProvider"

        available_providers = ort.get_all_providers()

        # Select appropriate provider
        if execution_provider in available_providers:
            self.__execution_providers = [execution_provider]
        else:
            self.__execution_providers = [
                next((p for p in TTS.PreferredProviders if p in available_providers), "CPUExecutionProvider")
            ]

        if verbose:
            print(f"Using providers: {self.__execution_providers}")
            print("Creating ONNX session for TTS...")

        def tts_infer_factor(session):
            return lambda **kwargs: session.run(None, kwargs)[0][0, 0]

        # Handle model path correctly
        model_file = (
            onnx_model_path
            if onnx_model_path.endswith(".onnx")
            else os.path.join(onnx_model_path, "kh.onnx")
        )

        self.__tts_infer = self.create_onnx_infer(
            infer_factor=tts_infer_factor,
            onnx_model_path=model_file,
            providers=self.__execution_providers,
            session_options=onnx_session_options,
            onnx_params=onnx_params,
        )
    # -----------------------------------------------------
    # Utility Methods
    # -----------------------------------------------------

    @staticmethod
    def __audio_float_to_int16(audio: np.ndarray, max_wav_value: float = 32767.0) -> np.ndarray:
        """Normalize audio and convert to int16 range."""
        audio_norm = audio * (max_wav_value / max(0.01, np.max(np.abs(audio))))
        audio_norm = np.clip(audio_norm, -max_wav_value, max_wav_value)
        return audio_norm.astype("int16")

    @staticmethod
    def __create_input(input_ids: np.ndarray) -> Dict[str, np.ndarray]:
        """Prepare ONNX input dictionary."""
        input_ids = np.expand_dims(input_ids, axis=0)
        input_lengths = np.array([input_ids.shape[1]], dtype=np.int64)
        scales = np.array([0.667, 1.0, 0.8], dtype=np.float32)

        return {
            "x": input_ids,
            "x_length": input_lengths,
            "scales": scales,
        }

    @staticmethod
    def __get_text_as_numpy(text: str) -> np.ndarray:
        """Convert text to tokenized numpy array."""
        text_norm = text_to_sequence(text=text)
        return np.array(text_norm, dtype=np.int64)

    # -----------------------------------------------------
    # Main Inference
    # -----------------------------------------------------

    def run(self, text: str) -> np.ndarray:
        """Generate audio from input text."""
        try:
            text_norm = self.__get_text_as_numpy(text=text)
            
            input_data = self.__create_input(input_ids=text_norm)
            
            audio = self.__tts_infer(**input_data)

            return self.__audio_float_to_int16(audio=audio)
        except Exception as e:
            raise RuntimeError(f"Error during audio generation: {e}")
