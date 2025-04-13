USE_KEYWORDS = True
STD_YACY_QUERY_TYPE = True # If True, then SOLR. If False, then JSON
PRINT_PROMPTS = False
USE_CHAT_SEQUENCE = False 
# if USE_CHAT_SEQUENCE is True, a sequence of messages will be passed to the llm with different roles
#   step 1: create a instruction message 
#       ChatMessage(role=MessageRole.SYSTEM, content=EXTERNAL_INSTRUCTION_CHAT_PROMPT)
#   step 2: iterate over the search result and pass each search result to llm
#       ChatMessage(role=MessageRole.ASSISTANT, content=f"[Search Result]\n{search_result.content}"))
#   step 3: send the query of the user to llm
#       ChatMessage(role=MessageRole.USER, content=query)
#  if False, just default EXTERNAL_CHAT_PROMPT is used with the context and the query