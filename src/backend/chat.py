import asyncio
from typing import AsyncIterator, List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.constants import get_model_string
from backend.db.chat import save_turn_to_db
from backend.llm.base import BaseLLM, EveryLLM
from backend.prompts import CHAT_PROMPT, HISTORY_QUERY_REPHRASE
from backend.related_queries import generate_related_queries
from backend.schemas import (
    BeginStream,
    ChatRequest,
    ChatResponseEvent,
    FinalResponseStream,
    Message,
    RelatedQueriesStream,
    SearchResult,
    SearchResultStream,
    StreamEndStream,
    StreamEvent,
    TextChunkStream,
)
from backend.search.search_service import perform_search
from backend.utils import is_local_model

import sys
sys.path.append("/workspace")
from user_prompts.external_prompts import EXTERNAL_CHAT_PROMPT, EXTERNAL_KEYWORD_PROMPT
from user_prompts.user_config import USE_KEYWORDS, PRINT_PROMPTS, STD_YACY_QUERY_TYPE
import os

def check_external_prompt() -> None:
    file_path = "/workspace/user_prompts/external_prompts.py"  # Ensure correct path

    if not os.path.exists(file_path):
        print(f" File '{file_path}' not found inside the container!")
    else:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            print("File content:\n", content)

async def extract_keywords(query: str, model_name: str)-> List[str]:
    llm_keyword = EveryLLM(model=model_name)
    fmt_ka_prompt = EXTERNAL_KEYWORD_PROMPT.format(
            my_query=query
        )
      
    full_response = ""
    response_gen = await llm_keyword.astream(fmt_ka_prompt)
    async for completion in response_gen:
        full_response += completion.delta or ""
    print("full_response", full_response) 
    clean_response = full_response.replace('"', '').strip()

    # Split the response into a list of keywords
    keywords = [keyword.strip() for keyword in clean_response.split(",") if keyword.strip()]
    return keywords


def rephrase_query_with_history(
    question: str, history: List[Message], llm: BaseLLM
) -> str:
    if not history:
        return question

    try:
        history_str = "\n".join(f"{msg.role}: {msg.content}" for msg in history)
        formatted_query = HISTORY_QUERY_REPHRASE.format(
            chat_history=history_str, question=question
        )
        question = llm.complete(formatted_query).text.replace('"', "")
        return question
    except Exception:
        raise HTTPException(
            status_code=500, detail="Model is at capacity. Please try again later."
        )


def format_context(search_results: List[SearchResult]) -> str:
    return "\n\n".join(
        [f"Citation {i+1}. {str(result)}" for i, result in enumerate(search_results)]
    )


async def stream_qa_objects(
    request: ChatRequest, session: Session
) -> AsyncIterator[ChatResponseEvent]:
    try:
        model_name = get_model_string(request.model)
        llm = EveryLLM(model=model_name)

        yield ChatResponseEvent(
            event=StreamEvent.BEGIN_STREAM,
            data=BeginStream(query=request.query),
        )
        # disable reprahse query with the history
        # query = rephrase_query_with_history(request.query, request.history, llm)

        query = request.query

        if PRINT_PROMPTS:
            check_external_prompt()

        if USE_KEYWORDS:
            keyword_list = await extract_keywords(query, model_name)
            print("keyword_list", keyword_list)
            search_response = await perform_search(keyword_list, use_keyword=True, solr_query_type=STD_YACY_QUERY_TYPE)
        else:
            search_response = await perform_search(query, use_keyword=False, solr_query_type=STD_YACY_QUERY_TYPE)

        search_results = search_response.results
        # images = search_response.images
        if not search_response.results:
            print("Es wurde kein Suchergebnise gefunden.")
            raise Exception("Es wurde kein Suchergebnise gefunden.")
        

        # Only create the task first if the model is not local
        related_queries_task = None
        if not is_local_model(request.model):
            related_queries_task = asyncio.create_task(
                generate_related_queries(query, search_results, llm)
            )

        yield ChatResponseEvent(
            event=StreamEvent.SEARCH_RESULTS,
            data=SearchResultStream(
                results=search_results,
                #images=images,
            ),
        )

        fmt_qa_prompt = EXTERNAL_CHAT_PROMPT.format(
            my_context=format_context(search_results),
            my_query=query,
        )

        full_response = ""
        response_gen = await llm.astream(fmt_qa_prompt)
        async for completion in response_gen:
            full_response += completion.delta or ""
            yield ChatResponseEvent(
                event=StreamEvent.TEXT_CHUNK,
                data=TextChunkStream(text=completion.delta or ""),
            )

        related_queries = await (
            related_queries_task
            if related_queries_task
            else generate_related_queries(query, search_results, llm)
        )

        yield ChatResponseEvent(
            event=StreamEvent.RELATED_QUERIES,
            data=RelatedQueriesStream(related_queries=related_queries),
        )

        thread_id = save_turn_to_db(
            session=session,
            thread_id=request.thread_id,
            user_message=request.query,
            assistant_message=full_response,
            model=request.model,
            search_results=search_results,
            image_results=None,
            related_queries=related_queries,
        )

        yield ChatResponseEvent(
            event=StreamEvent.FINAL_RESPONSE,
            data=FinalResponseStream(message=full_response),
        )

        yield ChatResponseEvent(
            event=StreamEvent.STREAM_END,
            data=StreamEndStream(thread_id=thread_id),
        )

    except Exception as e:
        detail = str(e)
        raise HTTPException(status_code=500, detail=detail)
