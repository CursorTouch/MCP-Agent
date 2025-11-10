from typing import Literal, Union, List
from pydantic import BaseModel, Field
from PIL.Image import Image
from io import BytesIO
import base64

class BaseMessage(BaseModel):
    role: Literal["system", "human", "ai"]
    content: str
    
    class Config:
        arbitrary_types_allowed = True

class SystemMessage(BaseMessage):
    role: Literal["system"] = "system" 
    content: str

    def __repr__(self) -> str:
        return f"SystemMessage(content={self.content})"

class HumanMessage(BaseMessage):
    role: Literal["user"] = "human"
    content: str

    def __repr__(self) -> str:
        return f"HumanMessage(content={self.content})"

class ImageMessage(HumanMessage):
    images: List[Union[Image, bytes, str]] = Field(default_factory=list)
    mime_type: str = "image/png"

    def _to_pillow(self, image: Union[Image, bytes, str]) -> Image:
        """Convert one image (any format) to a Pillow Image."""
        if isinstance(image, Image):
            return image
        elif isinstance(image, bytes):
            return Image.open(BytesIO(image))
        elif isinstance(image, str):
            return Image.open(BytesIO(base64.b64decode(image)))
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")

    def _to_bytes(self, image: Union[Image, bytes, str]) -> bytes:
        """Convert one image to raw bytes."""
        if isinstance(image, bytes):
            return image
        elif isinstance(image, str):
            return base64.b64decode(image)
        elif isinstance(image, Image):
            buffered = BytesIO()
            fmt = self.mime_type.split("/")[-1].upper()
            image.save(buffered, format=fmt, quality=80)
            return buffered.getvalue()
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")

    def _to_base64(self, image: Union[Image, bytes, str]) -> str:
        """Convert one image to base64 string."""
        if isinstance(image, str):
            return image
        img_bytes = self._to_bytes(image)
        return base64.b64encode(img_bytes).decode("utf-8")

    def convert_images(self, target_type: Literal["pillow", "bytes", "base64"]) -> None:
        """
        Convert all images in the list to the specified target type.
        Modifies self.images in-place.
        """
        converted = []

        for img in self.images:
            if target_type == "pillow":
                converted.append(self._to_pillow(img))
            elif target_type == "bytes":
                converted.append(self._to_bytes(img))
            elif target_type == "base64":
                converted.append(self._to_base64(img))
            else:
                raise ValueError(f"Unsupported target_type: {target_type}")
        return converted

    def scale_images(self, scale: float = 0.5) -> None:
        """Scale all Pillow images by given factor (auto-converts first if needed)."""
        if not (0 < scale < 1):
            raise ValueError("scale must be between 0 and 1")

        images = self.convert_images("pillow")

        scaled = []
        for image in images:
            size = (int(image.width * scale), int(image.height * scale))
            scaled.append(image.resize(size))
        self.images = scaled

    def __repr__(self) -> str:
        types = [type(i).__name__ for i in self.images]
        return f"ImageMessage(content={self.content!r}, images={types}, mime_type={self.mime_type})"

class AIMessage(BaseMessage):
    role: Literal["ai"] = "ai"
    content: str

    def __repr__(self) -> str:
        return f"AIMessage(content={self.content})"