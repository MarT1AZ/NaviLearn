# from langchain.llms import OpenAI
import asyncio
import logging
from pydantic import BaseModel
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
from datetime import datetime
import os
from youtube_search_tools import (
    fetch_comment_with_video_id,
    fetch_playlist_meta_data,
    fetch_video_id_from_a_playlist,
    fetch_video_information,
    search_revelant_video_or_playlist_ids_on_youtube,
)
# initialization
load_dotenv()






# class definition
class PlaylistProcessedItem(BaseModel):
    name : str
    content_summary : str
    bulletpoints : list[str]
    total_duration_hour : int
    channel : str
    first_published_year : str
    latest_update_year : str
    overall_comment_opinion_or_sentiment : str
    note : str



class VideoProcessedItem(BaseModel):
    name : str
    content_summary : str
    duration_minute : int
    channel : str
    date_published : str
    overall_comment_opinion_or_sentiment : str
    note : str

class ContentRecommendationList(BaseModel):
    recommended_videos: list[VideoProcessedItem]
    recommended_playlist: list[PlaylistProcessedItem]
    final_note : str


@function_tool
def get_current_date():
    return datetime.now().strftime("year %Y month %m day %d")


video_info_processor_agent = Agent(name = "video_info_processor_agent",
                                  
    instructions = """
You are a video info processing agent in a multi agent system for tech tutorial/material recommendation
the orchestator will call you and will provide video id and probably the original prompt by the user
You role is to fetch the information given the video id, summarize the content based on the video description and also comments sentiment (optional) then return result to the orchestator
You can use the (fetch_video_information) to obtain the information with the video id
I recommend you to summarize the content first to see whether the content match what the user want or not and also whether the video has comments or not (this is to optimize the API usage)
If it seem relevant, you can use the (fetch_comment_with_video_id) to obtain up to 10 comments and summarize the overall sentiment
Otherwise, just report in the note the reason you dont fetch the comments (tool error/irrelevantness/etc)
When summarize the comments, consider how people say/think of the content
final note : please state whether you recommend the video yes/no and state why in the note section
""",
    model="gpt-5.4-mini",
    tools = [fetch_video_information,fetch_comment_with_video_id],
    output_type=VideoProcessedItem)                    



video_playlist_processor_agent = Agent(name = "video_playlist_processor_agent",
                                  
    instructions = """
You are a playlist info processing agent in a multi agent system for tech tutorial/material recommendation
the orchestator will call you and will provide playlist id and probably the original prompt by the user

with the playlist id, you can
- fetch the list of video ids using (fetch_video_id_from_a_playlist)

with the video id, you can 
- fetch meta data of the playlist using (fetch_playlist_meta_data)
- fetch the video information using (fetch_video_information) 
- fetch comments using (fetch_comment_with_video_id), this tool fetch up to 10 comments

You main task
- read throught all the video's description snippet and summarize them
- summarize overall comment opinion/sentiment across the videos in the playlist
- give a bulletpoints showing key content
- first & latest update year
- sum up the total/estimate duration in hour (if the total duration is less than 1 just put 1)
- state whether you recommend the playlist yes/no and state why in the note section

Finally
- return summarized/processed and other information based on the given pydantic class to the orchestator

Note
- You have to go through all the videos in order to get the most accurate total duration
""",
    model="gpt-5.4-mini",
    tools = [fetch_playlist_meta_data,fetch_video_id_from_a_playlist,
             fetch_video_information,fetch_comment_with_video_id],
    output_type=PlaylistProcessedItem)  

# removed prompt : - You dont have to fetch comments from all video as some videos may be just a introductional or transitional video which have no meaningful content




orchestration_agent = Agent(name = "Tech Tutorials recommendation assistant",
              instructions="""
You are the orchestrator agent in a multi agent system for tech tutorial/material recommendation
You are an assistant that will provide a list youtube videos that suit the need of the user

you can compare or recommend the videos or playlists based on user's learning pace preference

When recommending a video, consider the following

- video duration (minute)
- video content (summarized)
- comment overall opinion/sentiment
- channel name
- date published (whether it is outdated or not)

When recommending a playlist, consider the following

- playlist content (summarized)
- comment overall opinion/sentiment
- last update date (whether it is outdated or not)

If there are no video that match the user preference, point out one with potential content

If you are not able to locate some information, please state it as a note

Short video should not be recommended unless the user ask for
Some video with just a few minute in length may be a short video or an introduction video to a playlist

Sometime, the user may ask to learn something which requires prerequisites
You should recommend those prerequisites and state why

============================================TOOLS========================================

1. search_revelant_video_or_playlist_ids_on_youtube

This tool allow you to fetch up to 5 video/playlist ids revelants to the query which you will have to send this to the agent
note 1 : try to use different queries if possible to avoid getting the same video
ืnote 2 : please try to provide for both video and playlist (only search up for 2 times for both type so it would not exhaust my API limit)

2. get current date 

The tool is used to get the current date so that you can check whether the video is outdated or not 
note 1 : content that are posted long ago are not alway considered outdated EG. python basic tutorial (the syntax does not change that much)

============================================TOOL AGENTS==============================

1. video_info_processor_agent

key infomation to sent : video_id , user query (paraphrase is ok)

This agent will retreive the info of the video with the id, return it 
the main content would be summarized for you
However, the comments may not be summarized for you
The agent may state that the comments are not fetched as the video may be irrelevance or there are no comment

2. video_playlist_processor_agent

key infomation to sent : playlist_id , user query (paraphrase is ok)

This agent will retreive the info of the playlist with the id, return it 
the main content would be summarized info and content bullet points for you

============================================FINAL NOTE==============================
1.If you could not find a video ro a playlist or the fetch videos or playlists are not being recommended, please state why in the final note section
""",
              model="gpt-5.4-mini",
              tools = [search_revelant_video_or_playlist_ids_on_youtube,
                       get_current_date,
                       video_playlist_processor_agent.as_tool(
                           tool_name = 'video_playlist_processor_agent',
                           tool_description = 'go through playlist videos, return with summarized, preprocessed info'
                       ),
                       video_info_processor_agent.as_tool(
                           tool_name = 'video_info_processor_agent',
                           tool_description = 'retrieve video information with id, return with summarized, preprocessed info'
                       )],
              output_type=ContentRecommendationList)





async def run_recommendation(query: str,cacheDictContext) -> tuple[ContentRecommendationList, int]:
    """
    Run the orchestration agent for a given query.
    Returns (ContentRecommendationList, total_tokens_used).
    """
    log_path = os.getenv("SAVE_LOG_PATH", ".")
    os.makedirs(log_path, exist_ok=True)
    query_truncated = query[:40]

 
    logging.basicConfig(
        level=logging.INFO,
        filename=os.path.join(log_path, f"QUERY_{query_truncated}.log"),
        filemode="w",
        format="%(name)s - %(levelname)s - %(message)s",
    )
    logging.info(f"[AGENT]: asking agent with query: {query}")
 
    result = await Runner.run(orchestration_agent, query,context=cacheDictContext)
 
    total_tokens = sum(
        r.usage.total_tokens for r in result.raw_responses if r.usage
    )
 
    return result.final_output, total_tokens