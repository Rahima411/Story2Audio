from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class TextRequest(_message.Message):
    __slots__ = ("text",)
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class AudioReply(_message.Message):
    __slots__ = ("audio_data", "format")
    AUDIO_DATA_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    audio_data: bytes
    format: str
    def __init__(self, audio_data: _Optional[bytes] = ..., format: _Optional[str] = ...) -> None: ...
