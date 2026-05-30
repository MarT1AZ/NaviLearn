
# About Navilearn

The system understands natural language queries and automatically retrieves relevant videos or playlists. It then analyzes, summarizes, and compares the content to recommend resources that best fit the user’s needs. This eliminating the manual process of searching through videos, reviewing playlists, or checking comments for quality and relevanceness.

## features
- video & playlist recommendation
- learn planner (In development)
  
## Requirements

 - Docker
 - OpenAI API key
 - Google Cloud API key
   
## Installation & Setup

The app can be install using docker and locally deployed

1. Clone the project
2. Locally deploy (user mode)
- Local deployment
   `docker compose up`
- Development deployment
   `docker compose -f docker-compose.dev.yml up`
3. ENV file setup

Inside The .ENV.example file put your API key
```
OPENAI_API_KEY="your key here"
YOUTUBE_API_KEY="your key here"
SAVE_LOG_PATH = "src/system_log"
CACHE_STORE_DIR = "src/cache_store"
```
The app stores cached search results in `src/cache_store/search_cache.json` and logs in `src/system_log/`.

Once installation & setup are completed, you can view the app on `http://localhost:8501`

Finally you can close / remove container using `docker compose down`

## Demo screenshot

Query : "Find a crash course for REST APIs under 2 hours"

<img width="490" height="852" alt="image" src="https://github.com/user-attachments/assets/393cdcc2-2c2e-4356-add5-f2c5d8bfb3b7" />

Query : "got any backend playlist for complete idiots"

<img width="501" height="745" alt="image" src="https://github.com/user-attachments/assets/ebfc26b0-91fd-4d0b-9766-fc267e1bf679" />

<img width="488" height="356" alt="image" src="https://github.com/user-attachments/assets/49837947-3ff8-4428-b37d-e2a7a84460e9" />

<img width="488" height="82" alt="image" src="https://github.com/user-attachments/assets/5eb47771-35ac-4e77-beb3-ff7947b9a820" />


## Future work

What i am aimming to do right now
- search result caching
- Interactive feedback system to refine recommendations through conversation
- Automatic re-search when users reject recommended content
- Optimizing token consumption for playlist analysis and recommendation
- Personalized learning planner

What is in my mind right now
- Project-based learning roadmap generator

















