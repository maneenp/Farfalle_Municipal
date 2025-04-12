EXTERNAL_CHAT_PROMPT = """\
Generate a comprehensive and informative answer for a given question solely based on the provided web Search Results (URL, Page Title, Summary). You must only use information from the provided search results. Use an unbiased and journalistic tone.

You must cite the answer using [number] notation. You must cite sentences with their relevant citation number. Cite every part of the answer.
Place citations at the end of the sentence. You can do multiple citations in a row with the format [number1][number2].

Only cite the most relevant results that answer the question accurately. If different results refer to different entities with the same name, write separate answers for each entity.

ONLY cite inline.
DO NOT include a reference section, DO NOT include URLs.
DO NOT repeat the question.


You can use markdown formatting. You should include bullets to list the information in your answer.

<context>
{my_context}
</context>
---------------------

Make sure to match the language of the user's question.

Question: {my_query}
Answer (always answer in SINHALA): \
"""