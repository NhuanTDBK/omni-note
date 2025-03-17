from typing import List
from PIL import Image
import torch
from paddleocr import PaddleOCR

from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg

from app.configs import Config


def get_vi_text_detector() -> Predictor:
    config = Cfg.load_config_from_name("vgg_seq2seq")
    config["weights"] = "https://vocr.vn/data/vietocr/vgg_seq2seq.pth"
    config["pretrain"] = "https://vocr.vn/data/vietocr/vgg_seq2seq.pth"
    config["device"] = "cuda" if torch.cuda.is_available() else "cpu"

    detector = Predictor(config)
    return detector


class PaddleOCRModel:
    def __init__(
        self,
        lang: str = "en",
        ocr_version: str = "PP-OCRv4",
        threshold: float = 0.8,
    ):
        self.is_external_detector = True if lang == "vi" else False
        if self.is_external_detector:
            self.detector = get_vi_text_detector()
        use_gpu = True if torch.cuda.is_available() else False
        self._paddle = PaddleOCR(
            use_angle_cls=False, lang=lang, use_gpu=use_gpu, ocr_version=ocr_version
        )
        self.threshold = threshold

    @staticmethod
    def from_config(config: Config):
        return PaddleOCRModel(
            # lang=config.OCR_LANG,
            # ocr_version=config.OCR_VERSION,
            # threshold=config.OCR_THRESHOLD,
        )

    def predict(self, img: bytes) -> List[str]:
        result = self._paddle.ocr(
            img, cls=False, det=True, rec=not self.is_external_detector
        )[:][:][0]

        if not self.is_external_detector:
            return [line[1][0] for line in result if line[1][1] >= self.threshold]
        # Create Boxes
        boxes = []
        for line in result:
            line = line[0]
            boxes.append(
                [[int(line[0][0]), int(line[0][1])], [int(line[2][0]), int(line[2][1])]]
            )

        boxes = boxes[::-1]

        EXPEND = 5
        for box in boxes:
            box[0][0] = box[0][0] - EXPEND
            box[0][1] = box[0][1] - EXPEND
            box[1][0] = box[1][0] + EXPEND
            box[1][1] = box[1][1] + EXPEND

        texts = []
        for box in boxes:
            cropped_image = img[box[0][1] : box[1][1], box[0][0] : box[1][0]]

            try:
                cropped_image = Image.fromarray(cropped_image)
            except:
                continue

            rec_result = self.detector.predict(cropped_image)

            text = rec_result  # [0]

            texts.append(text)

        return texts
