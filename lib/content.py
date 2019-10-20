from dataclasses import dataclass, field
from typing import Optional, List, Dict

from .utils import EncryptedFile, ImageInfo, FileInfo, AudioInfo, VideoInfo, LocationInfo, PreviousRoom, Invite


@dataclass
class ContentBase:
    pass


@dataclass
class MessageContentBase(ContentBase):
    body: str
    msgtype: str


@dataclass
class MTextContent(MessageContentBase):
    format: Optional[str] = None
    formatted_body: Optional[str] = None
    msgtype = 'm.text'


@dataclass
class MEmoteContent(MTextContent):
    msgtype = 'm.emote'


@dataclass
class MNoticeContent(MTextContent):
    msgtype = 'm.notice'


@dataclass
class MImageContent(MessageContentBase):
    msgtype = 'm.image'
    info: ImageInfo
    url: Optional[str] = None
    file: Optional[EncryptedFile] = None


@dataclass
class MFileContent(MessageContentBase):
    msgtype = 'm.file'
    filename: str
    info: FileInfo
    url: Optional[str] = None
    file: Optional[EncryptedFile] = None


@dataclass
class MAudioContent(MessageContentBase):
    msgtype = 'm.audio'
    info: AudioInfo
    url: Optional[str] = None
    file: Optional[EncryptedFile] = None


@dataclass
class MLocationContent(MessageContentBase):
    msgtype = 'm.location'
    geo_uri: str
    info: LocationInfo


@dataclass
class MVideoContent(MessageContentBase):
    msgtype = 'm.video'
    info: VideoInfo
    url: Optional[str] = None
    file: Optional[EncryptedFile] = None


@dataclass
class PresenceContent(ContentBase):
    presence: str
    last_active_ago: int
    currently_active: bool
    avatar_url: Optional[str] = None
    displayname: Optional[str] = None
    status_message: Optional[str] = None


@dataclass
class MRoomAliasesContent(ContentBase):
    aliases: List[str]


@dataclass
class MRoomCanonicalAliasContent(ContentBase):
    alias: str


@dataclass
class MRoomCreateContent(ContentBase):
    creator: str
    room_version: Optional[str] = '1'
    m_federate: Optional[bool] = True
    predecessor: Optional[PreviousRoom] = None


@dataclass
class MRoomJoinRulesContent(ContentBase):
    join_rule: str


@dataclass
class MRoomMemberContent(ContentBase):
    membership: str
    is_direct: bool
    third_party_invite: Optional[Invite] = None
    avatar_url: Optional[str] = None
    displayname: str = None


@dataclass
class MRoomPowerLevelsContent(ContentBase):
    ban: int = 50
    events: Dict[str, int] = field(default_factory=dict)
    events_default: int = 0
    invite: int = 50
    kick: int = 50
    redact: int = 50
    state_default: int = 50
    users: Dict[str, int] = field(default_factory=dict)
    users_default: int = 0
    notifications: Dict[str, int] = field(default={'room': 50})


@dataclass
class MRoomRedactionContent(ContentBase):
    reason: str
