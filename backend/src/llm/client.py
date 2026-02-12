from langchain_community.llms import Ollama

llm = Ollama(
    model="llama3",
    temperature=0.2,
    top_k=40,
    top_p=0.9,
    num_ctx=4096,
    system="You must return only valid JSON. Do not include any explanation, note, markdown, or text before or after the JSON object. Only return JSON."
)