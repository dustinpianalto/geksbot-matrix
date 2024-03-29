from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class JSONWebKey:
    key_opts: List[str]
    k: str
    ext: bool = True
    alg: str = 'A256CTR'
    kty: str = 'oct'


@dataclass
class EncryptedFile:
    url: str
    key: JSONWebKey
    iv: str
    hashes: Dict[str, str]
    v: str = 'v2'


@dataclass
class ImageInfoBase:
    h: int
    w: int
    mimetype: str
    size: int


@dataclass
class ImageInfo(ImageInfoBase):
    thumbnail_info: ImageInfoBase
    thumbnail_url: Optional[str] = None
    thumbnail_file: Optional[EncryptedFile] = None


@dataclass
class FileInfo:
    mimetype: str
    size: int
    thumbnail_info: ImageInfoBase
    thumbnail_url: Optional[str] = None
    thumbnail_file: Optional[EncryptedFile] = None


@dataclass
class AudioInfo:
    duration: int
    mimetype: str
    size: int


@dataclass
class LocationInfo:
    thumbnail_info: ImageInfoBase
    thumbnail_url: Optional[str] = None
    thumbnail_file: Optional[EncryptedFile] = None


@dataclass
class VideoInfo(ImageInfoBase):
    duration: int
    thumbnail_info: ImageInfoBase
    thumbnail_url: Optional[str] = None
    thumbnail_file: Optional[EncryptedFile] = None


@dataclass
class PreviousRoom:
    room_id: str
    event_id: str


@dataclass
class Signed:
    mxid: str
    signatures: Dict[str, Dict[str, str]]
    token: str


@dataclass
class Invite:
    display_name: str
    signed: Signed
