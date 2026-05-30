
import isodate
from dataclasses import dataclass, field


@dataclass
class SearchItemCacheDictContext:
    videoItemDict: dict = field(default_factory=dict)
    playlistItemDict: dict = field(default_factory=dict)


@dataclass
class Comment:
    comment_text: str
    like_count: int
    published_at: str
    updated_at: str

    @classmethod
    def from_json(cls, comment_json):
        top_level = comment_json["snippet"]["topLevelComment"]["snippet"]
        return cls(
            comment_text=top_level["textOriginal"],
            like_count=top_level["likeCount"],
            published_at=top_level["publishedAt"],
            updated_at=top_level["updatedAt"],
        )



@dataclass
class CommentThreads:
    previous_page_token: str | None = None
    next_page_token: str | None = None
    comments: list[Comment] = field(default_factory=list)

    def __init__(self, commentThread_json):
        self.previous_page_token = commentThread_json.get("prevPageToken")
        self.next_page_token = commentThread_json.get("nextPageToken")
        self.comments = [Comment.from_json(item) for item in commentThread_json.get("items", [])]



@dataclass
class VideoInfoItem:
    video_id: str = ""
    title: str = ""
    channel_name: str = ""
    publish_time: str = ""
    description_snippet: str = ""
    duration_minute: int | None = None
    viewCount: int | None = None
    likeCount: int | str | None = None
    likeCount_available: bool = False
    favoriteCount: int | None = None
    commentCount: int | None = None

    @classmethod
    def from_json(cls, video_json):
        description = video_json["snippet"]["description"]
        if len(description) >= 100:
            description_snippet = description[0:100] + "..."
        else:
            description_snippet = description

        video_statistics = video_json["statistics"]
        like_count = video_statistics.get("likeCount")
        like_count_available = like_count is not None

        return cls(
            video_id=video_json["id"],
            title=video_json["snippet"]["title"],
            channel_name=video_json["snippet"]["channelTitle"],
            publish_time=video_json["snippet"]["publishedAt"],
            description_snippet=description_snippet,
            duration_minute=int(isodate.parse_duration(video_json["contentDetails"]["duration"]).total_seconds() // 60),
            viewCount=int(video_statistics["viewCount"]),
            likeCount=int(like_count) if like_count_available else "not available",
            likeCount_available=like_count_available,
            favoriteCount=int(video_statistics["favoriteCount"]),
            commentCount=int(video_statistics["commentCount"]),
        )

    def has_full_info(self) -> bool:
        return all(
            [
                self.video_id,
                self.title,
                self.channel_name,
                self.publish_time,
                self.description_snippet,
                self.duration_minute is not None,
                self.viewCount is not None,
                self.favoriteCount is not None,
                self.commentCount is not None,
            ]
        )


@dataclass
class PlaylistInfoItem:
    playlist_id: str = ""
    title: str = ""
    channel_name: str = ""
    description: str = ""
    video_ids: list[str] = field(default_factory=list)

    def has_metadata(self) -> bool:
        return bool(self.title and self.channel_name and self.description)

    def has_video_ids(self) -> bool:
        return bool(self.video_ids)





