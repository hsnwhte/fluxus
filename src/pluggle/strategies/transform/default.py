from pluggle.enums import ContentFormat
from pluggle.models.dto import TransformableData, TransformedData


class TransformStrategySamplePassthrough:
    def __init__(
        self, *, target_format: ContentFormat, data: TransformableData, **kwargs
    ):
        self.target_format = target_format
        self.data = data

    def transform(self) -> TransformedData:
        return TransformedData(content=self.data.content)
