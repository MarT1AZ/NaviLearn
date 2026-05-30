import json
import logging
import os

import requests
from agents import RunContextWrapper, function_tool
from dotenv import load_dotenv

from caching import CommentThreads, PlaylistInfoItem, SearchItemCacheDictContext, VideoInfoItem

load_dotenv()


def _get_cache_context(ctx):
    """Return the shared cache object from the Agents wrapper, if present."""
    if ctx is None:
        return None

    if hasattr(ctx, "context"):
        return ctx.context

    return ctx


def _success_header(tool_name: str) -> str:
    return f"[TOOL-{tool_name}][SUCCESS]"


def _failure_header(tool_name: str) -> str:
    return f"[TOOL-{tool_name}][FAILURE]"


def _return_success(tool_name: str, body: str) -> str:
    return f"{_success_header(tool_name)}\n{body}".strip()


def _return_failure(tool_name: str, body: str) -> str:
    return f"{_failure_header(tool_name)}\n{body}".strip()


@function_tool
def search_revelant_video_or_playlist_ids_on_youtube(query: str):
    tool_name = "search_revelant_video_ids_on_youtube"
    logging.info(f"[TOOL-{tool_name}]: starting YouTube search for query=%r", query)

    search_url = "https://www.googleapis.com/youtube/v3/search"
    search_params = {
        "part": "id",
        "q": query,
        "type": "video,playlist",
        "maxResults": 2,
        "key": os.getenv("YOUTUBE_API_KEY"),
    }

    try:
        response = requests.get(search_url, params=search_params, timeout=20)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        error_string = f"HTTP error with status code: {response.status_code}"
        logging.warning(f"[TOOL-{tool_name}]: %s", error_string)
        return _return_failure(tool_name, error_string)
    except requests.exceptions.RequestException as err:
        error_string = f"Request failed: {err}"
        logging.warning(f"[TOOL-{tool_name}]: %s", error_string)
        return _return_failure(tool_name, error_string)
    except Exception as err:
        error_string = f"Unexpected error: {err}"
        logging.warning(f"[TOOL-{tool_name}]: %s", error_string)
        return _return_failure(tool_name, error_string)

    response_json = response.json()
    id_items = response_json.get("items", [])
    logging.info(f"[TOOL-{tool_name}]: found %d search results", len(id_items))

    return_id_lines = []
    for i, item in enumerate(id_items):
        item_type = item["id"]["kind"]
        if item_type == "youtube#playlist":
            item_id = item["id"]["playlistId"]
            return_id_lines.append(f"{i + 1}. playlist id : {item_id}")
        elif item_type == "youtube#video":
            item_id = item["id"]["videoId"]
            return_id_lines.append(f"{i + 1}. video id : {item_id}")

    logging.info(f"[TOOL-{tool_name}]: search completed successfully for query=%r", query)
    return _return_success(tool_name, "\n".join(return_id_lines))


@function_tool
def fetch_video_information(ctx: RunContextWrapper[SearchItemCacheDictContext], video_id: str):
    tool_name = "fetch_video_information"
    cache_context = _get_cache_context(ctx)
    video_cache = getattr(cache_context, "videoItemDict", None) if cache_context else None

    if video_cache is not None and video_id in video_cache:
        cached_item = video_cache[video_id]
        if cached_item.has_full_info():
            logging.info(f"[TOOL-{tool_name}]: cache hit for video_id=%s", video_id)
            body = "Returned cached video details:\n" + json.dumps(cached_item.__dict__, indent=2)
            return _return_success(tool_name, body)

    logging.info(f"[TOOL-{tool_name}]: cache miss, fetching video_id=%s from YouTube", video_id)

    video_info_fetch_url = "https://www.googleapis.com/youtube/v3/videos"
    video_search_params = {
        "part": "snippet,statistics,contentDetails",
        "id": video_id,
        "key": os.getenv("YOUTUBE_API_KEY"),
    }

    try:
        response = requests.get(video_info_fetch_url, params=video_search_params, timeout=20)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        error_string = f"HTTP error with status code: {response.status_code}"
        logging.warning(f"[TOOL-{tool_name}]: %s", error_string)
        return _return_failure(tool_name, error_string)
    except requests.exceptions.RequestException as err:
        error_string = f"Request failed: {err}"
        logging.warning(f"[TOOL-{tool_name}]: %s", error_string)
        return _return_failure(tool_name, error_string)
    except Exception as err:
        error_string = f"Unexpected error: {err}"
        logging.warning(f"[TOOL-{tool_name}]: %s", error_string)
        return _return_failure(tool_name, error_string)

    response_json = response.json()
    items = response_json.get("items", [])
    if not items:
        error_string = f"No video data found for video id: {video_id}"
        logging.warning(f"[TOOL-{tool_name}]: %s", error_string)
        return _return_failure(tool_name, error_string)

    video_item = VideoInfoItem.from_json(items[0])
    if video_cache is not None:
        video_cache[video_id] = video_item
        if cache_context is not None and hasattr(cache_context, "save_to_disk"):
            cache_context.save_to_disk()

    logging.info(f"[TOOL-{tool_name}]: video details fetched successfully for video_id=%s", video_id)
    body = "Fetched video details:\n" + json.dumps(video_item.__dict__, indent=2)
    return _return_success(tool_name, body)


@function_tool
def fetch_comment_with_video_id(video_id: str, video_name: str):
    tool_name = "fetch_comment_with_video_id"
    logging.info(
        f"[TOOL-{tool_name}]: fetching comments for video_id=%s video_name=%r",
        video_id,
        video_name,
    )

    fetch_url = "https://www.googleapis.com/youtube/v3/commentThreads"
    fetch_params = {
        "part": "snippet",
        "maxResults": 20,
        "order": "relevance",
        "videoId": video_id,
        "key": os.getenv("YOUTUBE_API_KEY"),
    }

    try:
        response = requests.get(fetch_url, params=fetch_params, timeout=20)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        error_string = f"HTTP error with status code: {response.status_code}"
        logging.warning(f"[TOOL-{tool_name}]: %s", error_string)
        return _return_failure(tool_name, error_string)
    except requests.exceptions.RequestException as err:
        error_string = f"Request failed: {err}"
        logging.warning(f"[TOOL-{tool_name}]: %s", error_string)
        return _return_failure(tool_name, error_string)
    except Exception as err:
        error_string = f"Unexpected error: {err}"
        logging.warning(f"[TOOL-{tool_name}]: %s", error_string)
        return _return_failure(tool_name, error_string)

    response_json = response.json()
    items = response_json.get("items", [])
    logging.info(f"[TOOL-{tool_name}]: fetched %d comment threads for video_id=%s", len(items), video_id)

    if not items:
        return _return_success(tool_name, f"No comments found for video id: {video_id}")

    comment_thread = CommentThreads(response_json)
    return_string = f"Top relevant comments for video id: {video_id}\n\n"
    for index, comment in enumerate(comment_thread.comments, 1):
        return_string += f"{index}. text: {comment.comment_text}\n"

    return _return_success(tool_name, return_string)


@function_tool
def fetch_video_id_from_a_playlist(ctx: RunContextWrapper[SearchItemCacheDictContext], playlist_id: str):
    tool_name = "fetch_video_id_from_a_playlist"
    cache_context = _get_cache_context(ctx)
    playlist_cache = getattr(cache_context, "playlistItemDict", None) if cache_context else None

    if playlist_cache is not None and playlist_id in playlist_cache:
        cached_item = playlist_cache[playlist_id]
        if getattr(cached_item, "video_ids", None):
            logging.info(f"[TOOL-{tool_name}]: cache hit for playlist_id=%s", playlist_id)
            body = "\n".join(
                f"{i + 1}. video id : {video_id}"
                for i, video_id in enumerate(cached_item.video_ids)
            )
            return _return_success(tool_name, body)

    logging.info(f"[TOOL-{tool_name}]: cache miss, fetching playlist video ids for playlist_id=%s", playlist_id)

    fetch_url = "https://youtube.googleapis.com/youtube/v3/playlistItems"
    fetch_params = {
        "part": "snippet",
        "playlistId": playlist_id,
        "maxResults": 50,
        "key": os.getenv("YOUTUBE_API_KEY"),
    }

    try:
        response = requests.get(fetch_url, params=fetch_params, timeout=20)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        error_string = f"HTTP error with status code: {response.status_code}"
        logging.warning(f"[TOOL-{tool_name}]: %s", error_string)
        return _return_failure(tool_name, error_string)
    except requests.exceptions.RequestException as err:
        error_string = f"Request failed: {err}"
        logging.warning(f"[TOOL-{tool_name}]: %s", error_string)
        return _return_failure(tool_name, error_string)
    except Exception as err:
        error_string = f"Unexpected error: {err}"
        logging.warning(f"[TOOL-{tool_name}]: %s", error_string)
        return _return_failure(tool_name, error_string)

    response_json = response.json()
    items = response_json.get("items", [])
    logging.info(f"[TOOL-{tool_name}]: fetched %d playlist entries for playlist_id=%s", len(items), playlist_id)

    video_ids = [item["snippet"]["resourceId"]["videoId"] for item in items]
    if playlist_cache is not None:
        playlist_item = playlist_cache.get(playlist_id)
        if playlist_item is None:
            playlist_item = PlaylistInfoItem(playlist_id=playlist_id)
            playlist_cache[playlist_id] = playlist_item
        playlist_item.video_ids = video_ids
        if cache_context is not None and hasattr(cache_context, "save_to_disk"):
            cache_context.save_to_disk()

    body = "\n".join(f"{i + 1}. video id : {video_id}" for i, video_id in enumerate(video_ids))
    return _return_success(tool_name, body)


@function_tool
def fetch_playlist_meta_data(ctx: RunContextWrapper[SearchItemCacheDictContext], playlist_id: str):
    tool_name = "fetch_playlist_meta_data"
    cache_context = _get_cache_context(ctx)
    playlist_cache = getattr(cache_context, "playlistItemDict", None) if cache_context else None

    if playlist_cache is not None and playlist_id in playlist_cache:
        cached_item = playlist_cache[playlist_id]
        if cached_item.has_metadata():
            logging.info(f"[TOOL-{tool_name}]: cache hit for playlist_id=%s", playlist_id)
            body = (
                f"Playlist title : {cached_item.title}\n"
                f"Channel : {cached_item.channel_name}\n"
                f"description : {cached_item.description}"
            )
            return _return_success(tool_name, body)

    logging.info(f"[TOOL-{tool_name}]: cache miss, fetching metadata for playlist_id=%s", playlist_id)

    fetch_url = "https://youtube.googleapis.com/youtube/v3/playlists"
    fetch_params = {
        "part": "snippet",
        "id": playlist_id,
        "key": os.getenv("YOUTUBE_API_KEY"),
    }

    try:
        response = requests.get(fetch_url, params=fetch_params, timeout=20)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        error_string = f"HTTP error with status code: {response.status_code}"
        logging.warning(f"[TOOL-{tool_name}]: %s", error_string)
        return _return_failure(tool_name, error_string)
    except requests.exceptions.RequestException as err:
        error_string = f"Request failed: {err}"
        logging.warning(f"[TOOL-{tool_name}]: %s", error_string)
        return _return_failure(tool_name, error_string)
    except Exception as err:
        error_string = f"Unexpected error: {err}"
        logging.warning(f"[TOOL-{tool_name}]: %s", error_string)
        return _return_failure(tool_name, error_string)

    response_json = response.json()
    items = response_json.get("items", [])
    if not items:
        error_string = f"No playlist metadata found for playlist id: {playlist_id}"
        logging.warning(f"[TOOL-{tool_name}]: %s", error_string)
        return _return_failure(tool_name, error_string)

    metadata_items = items[0]["snippet"]
    playlist_item = PlaylistInfoItem(
        playlist_id=playlist_id,
        title=metadata_items["title"],
        channel_name=metadata_items["channelTitle"],
        description=metadata_items["description"],
    )

    if playlist_cache is not None:
        existing_item = playlist_cache.get(playlist_id)
        if existing_item is not None:
            if not existing_item.title:
                existing_item.title = playlist_item.title
            if not existing_item.channel_name:
                existing_item.channel_name = playlist_item.channel_name
            if not existing_item.description:
                existing_item.description = playlist_item.description
        else:
            playlist_cache[playlist_id] = playlist_item
        if cache_context is not None and hasattr(cache_context, "save_to_disk"):
            cache_context.save_to_disk()

    logging.info(f"[TOOL-{tool_name}]: metadata fetched successfully for playlist_id=%s", playlist_id)
    body = (
        f"Playlist title : {playlist_item.title}\n"
        f"Channel : {playlist_item.channel_name}\n"
        f"description : {playlist_item.description}"
    )
    return _return_success(tool_name, body)
