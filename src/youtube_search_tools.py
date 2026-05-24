import isodate
import os
import requests
from dotenv import load_dotenv
from agents import function_tool
from datetime import datetime
import logging
import json




class Comment():
    def __init__(self,comment_json):
    
        self.comment_text = comment_json['snippet']['topLevelComment']['snippet']['textOriginal']
        self.like_count = comment_json['snippet']['topLevelComment']['snippet']['likeCount']
        self.published_at = comment_json['snippet']['topLevelComment']['snippet']['publishedAt']
        self.updated_at = comment_json['snippet']['topLevelComment']['snippet']['updatedAt']



class CommentThreads():
    def __init__(self,commentThread_json):

        self.previous_page_token : commentThread_json['prevPageToken']
        self.next_page_token : commentThread_json['nextPageToken']
        self.comments = []
        for comment_item_json in commentThread_json['items']:
            self.comments.append(Comment(comment_item_json))



class VideoInfoItem():

    def __init__(self,video_json):
        self.video_id = video_json['id']
        self.title = video_json['snippet']['title']
        self.channel_name = video_json['snippet']['channelTitle']
        self.publish_time = video_json['snippet']['publishedAt']

        if(len(video_json['snippet']['description']) >= 100):
            self.description_snippet = video_json['snippet']['description'][0:100] + "..."
        else:
            self.description_snippet = video_json['snippet']['description']



        self.duration_minute = int(isodate.parse_duration(video_json['contentDetails']['duration']).total_seconds()//60)

        video_statistics = video_json['statistics']
        self.viewCount = int(video_statistics['viewCount'])

        self.likeCount = None
        self.likeCount_available = False
        if('likeCount' in video_statistics):
            self.likeCount = "not available"
        else:
            self.likeCount_available = True
            self.likeCount = int(video_statistics['likeCount'])

        self.favoriteCount = int(video_statistics['favoriteCount'])
        self.commentCount = int(video_statistics['commentCount'])


class SearchResult():

    def __init__(self,search_response_json):
        self.previous_page_token : search_response_json['prevPageToken']
        self.next_page_token : search_response_json['nextPageToken']
        self.VideoList = []















# @function_tool
# def search_revelant_video_ids_on_youtube(query : str):

#     # logging attributes
#     tool_names = "search_revelant_video_ids_on_youtube"

#     logging.info(f"[TOOL-{tool_names}]:Attempting to search on youtube with {query}")

#     search_url = "https://www.googleapis.com/youtube/v3/search"

#     search_params = {
#         "part": "id",
#         "q": query,
#         "type": "video",
#         "maxResults": 10, # 2 for test 10 for production
#         "key": os.getenv('YOUTUBE_API_KEY')
#     }

#     try:
#         response = requests.get(
#             search_url,
#             params=search_params,
#             timeout=20
#         )
#         response.raise_for_status()
#     except requests.exceptions.HTTPError as err:
#         error_string = f"[TOOL-{tool_names}]: HTTP error with status code: {response.status_code}"
#         logging.warning(error_string)
#         return error_string

#     except requests.exceptions.RequestException as err:
#         error_string = f"[TOOL-{tool_names}]: fetching failed : {str(err)}"
#         logging.warning(error_string)
#         return error_string
#     except Exception as err:
#         error_string = f"[TOOL-{tool_names}]: error : {str(err)}"
#         logging.warning(error_string)
#         return error_string

#     response_json = response.json()
#     id_items = response_json['items']
#     id_list = []
#     for item in id_items:
#         id_list.append(item['id']['videoId'])

#     logging.info(f"[TOOL-{tool_names}]:fetching in total {len(id_list)} video id entries for query {query}")

    
#     return_id_lines = []

#     for i, id in enumerate(id_list):
#         return_id_lines.append(f"{i + 1}.video id : {id}")

#     return_string = "\n".join(return_id_lines)

#     return return_string



















@function_tool
def search_revelant_video_or_playlist_ids_on_youtube(query : str):

    # logging attributes
    tool_names = "search_revelant_video_ids_on_youtube"

    logging.info(f"[TOOL-{tool_names}]:Attempting to search on youtube with {query}")

    search_url = "https://www.googleapis.com/youtube/v3/search"

    search_params = {
        "part": "id",
        "q": query,
        "type": "video,playlist",
        "maxResults": 5, # 2 for test 10 for production
        "key": os.getenv('YOUTUBE_API_KEY')
    }

    try:
        response = requests.get(
            search_url,
            params=search_params,
            timeout=20
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        error_string = f"[TOOL-{tool_names}]: HTTP error with status code: {response.status_code}"
        logging.warning(error_string)
        return error_string

    except requests.exceptions.RequestException as err:
        error_string = f"[TOOL-{tool_names}]: fetching failed : {str(err)}"
        logging.warning(error_string)
        return error_string
    except Exception as err:
        error_string = f"[TOOL-{tool_names}]: error : {str(err)}"
        logging.warning(error_string)
        return error_string

    response_json = response.json()
    id_items = response_json['items']

    logging.info(f"[TOOL-{tool_names}]:fetching in total {len(id_items)} id entries for query {query}")

    return_id_lines = []

    for i in range(len(id_items)):

        item_type = id_items[i]['id']['kind']

        if(item_type == "youtube#playlist"):
            id = id_items[i]['id']['playlistId']
            return_id_lines.append(f"{i + 1}.playlist id : {id}")
        elif(item_type == "youtube#video"):
            id = id_items[i]['id']['videoId']
            return_id_lines.append(f"{i + 1}.video id : {id}")

    return_string = "\n".join(return_id_lines)

    return return_string


























@function_tool
def fetch_video_information(video_id : str):

    tool_names = "fetch_video_information"

    logging.info(f"[TOOL-{tool_names}]:fetching general information for video id : {video_id}")

    video_info_fetch_url = "https://www.googleapis.com/youtube/v3/videos"


    video_search_params = {
        "part": "snippet,statistics,contentDetails",
        "id": video_id,
        "key": os.getenv('YOUTUBE_API_KEY')
    }


    try:
        response = requests.get(
        video_info_fetch_url,
        params=video_search_params,
        timeout=20
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        error_string = f"[TOOL-{tool_names}]: HTTP error with status code: {response.status_code}"
        logging.warning(error_string)
        return error_string

    except requests.exceptions.RequestException as err:
        error_string = f"[TOOL-{tool_names}]: fetching failed : {str(err)}"
        logging.warning(error_string)
        return error_string
    except Exception as err:
        error_string = f"[TOOL-{tool_names}]: error : {str(err)}"
        logging.warning(error_string)
        return error_string
    
    response_json = response.json()

    logging.info(f"[TOOL-{tool_names}]:fetching infomation successfully for the video with id : {video_id }")

    InfoItem = VideoInfoItem(response_json['items'][0])
    return json.dumps(InfoItem.__dict__)

  


























@function_tool
def fetch_comment_with_video_id(video_id : str, video_name : str):

    tool_names = "fetch_comment_with_video_id"

    fetch_url = "https://www.googleapis.com/youtube/v3/commentThreads"

    logging.info(f"[TOOL-{tool_names}]:fetching comments of the video with id : {video_id }, video name : {video_name}")
    fetch_params = {
        "part": "snippet",
        "maxResults": 20,
        "order": "relevance",
        "videoId": video_id,
        "key": os.getenv('YOUTUBE_API_KEY')
    }


    try:
        response = requests.get(
            fetch_url,
            params=fetch_params,
            timeout=20
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        error_string = f"[TOOL-{tool_names}]: HTTP error with status code: {response.status_code}"
        logging.warning(error_string)
        return error_string

    except requests.exceptions.RequestException as err:
        error_string = f"[TOOL-{tool_names}]: fetching failed : {str(err)}"
        logging.warning(error_string)
        return error_string
    except Exception as err:
        error_string = f"[TOOL-{tool_names}]: error : {str(err)}"
        logging.warning(error_string)
        return error_string
    


 
    response_json = response.json()
    logging.info(f"[TOOL-{tool_names}]:fetching comments successfully for the video with id : {video_id }")

    if(len(response_json['items']) == 0):
        logging.info(f"[TOOL-{tool_names}]:no comments found for video id : {video_id }")
        return "No Comments Found"
    else:
        logging.info(f"[TOOL-{tool_names}]:found {len(response_json['items'])} comments for video id : {video_id }")


    comment_thread = CommentThreads(response_json)
    return_string = f"top 10 revelance comment for video id = {video_id}\n\n"

    for id, comment in enumerate(comment_thread.comments):

#         return_string = return_string + f"""{id + 1}. 
# text : {comment.comment_text}
# like count : {comment.like_count}
# published date : {comment.published_at}
# updated date : {comment.updated_at}\n"""
        
        return_string = return_string + f"""{id + 1}. 
text : {comment.comment_text}\n"""
        
        


    return return_string


















@function_tool
def fetch_video_id_from_a_playlist(playlist_id : str):

    tool_names = "fetch_video_id_from_a_playlist"

    logging.info(f"[TOOL-{tool_names}]:fetching video id list for palylist id : {playlist_id}")

    fetch_url = "https://youtube.googleapis.com/youtube/v3/playlistItems"


    fetch_params = {
        "part": "snippet",
        "playlistId": playlist_id,
        "maxResults":50,
        "key": os.getenv('YOUTUBE_API_KEY')
    }


    try:
        response = requests.get(
        fetch_url,
        params=fetch_params,
        timeout=20
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        error_string = f"[TOOL-{tool_names}]: HTTP error with status code: {response.status_code}"
        logging.warning(error_string)
        return error_string

    except requests.exceptions.RequestException as err:
        error_string = f"[TOOL-{tool_names}]: fetching failed : {str(err)}"
        logging.warning(error_string)
        return error_string
    except Exception as err:
        error_string = f"[TOOL-{tool_names}]: error : {str(err)}"
        logging.warning(error_string)
        return error_string
    
    response_json = response.json()
    id_items = response_json['items']

    logging.info(f"[TOOL-{tool_names}]:fetching in total {len(id_items)} from the playlist id {playlist_id}")

    return_id_lines = []

    for i in range(len(id_items)):

        id = id_items[i]['snippet']['resourceId']['videoId']
        return_id_lines.append(f"{i + 1}.video id : {id}")

    return_string = "\n".join(return_id_lines)

    return return_string
















@function_tool
def fetch_playlist_meta_data(playlist_id : str):

    tool_names = "fetch_playlist_meta_data"

    logging.info(f"[TOOL-{tool_names}]:fetching meta data for playlist id : {playlist_id}")

    fetch_url = "https://youtube.googleapis.com/youtube/v3/playlists"


    fetch_params = {
        "part": "snippet",
        "id": playlist_id,
        "key": os.getenv('YOUTUBE_API_KEY')
    }

    try:
        response = requests.get(
        fetch_url,
        params=fetch_params,
        timeout=20
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        error_string = f"[TOOL-{tool_names}]: HTTP error with status code: {response.status_code}"
        logging.warning(error_string)
        return error_string

    except requests.exceptions.RequestException as err:
        error_string = f"[TOOL-{tool_names}]: fetching failed : {str(err)}"
        logging.warning(error_string)
        return error_string
    except Exception as err:
        error_string = f"[TOOL-{tool_names}]: error : {str(err)}"
        logging.warning(error_string)
        return error_string

    response_json = response.json()
    metadata_items = response_json['items'][0]['snippet']

    logging.info(f"[TOOL-{tool_names}]:fetching meta data seccussfully from the playlist id {playlist_id}")

    return_string = f"""
Playlist title : {metadata_items["title"]}
Channel : {metadata_items["channelTitle"]}
description : {metadata_items["description"]}
"""
    
    return return_string


