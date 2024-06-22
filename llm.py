import openai  # TODO: add support for arbitrary GPTs

#openai_key: "str|None" = os.environ.get("OPENAI_API_KEY")
openai_key = "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"
if openai_key is None:
    raise Exception("OPENAI_API_KEY environment variable not set.")
openai.api_key = openai_key

OPENAI_MODEL = "gpt-3.5-turbo-0125"

openai_client = openai.OpenAI(
    base_url="https://gateway.ai.cloudflare.com/v1/09fec33cfb1d5c316f4121dc37140834/openai/openai",
    api_key=openai_key
)
print("Successfully obtained openai client")

def query_openai(prompt: str, history:list|None = None) -> str:
    """
    Ask openai a question in the form a string, get a response in the form of a string.
    """
    messages = history if history is not None else []
    messages.append({"role": "user", "content": prompt})
    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL, messages=messages
    )
    result = response.choices[0].message.content
    if result is None:
        raise Exception("Openai produced null response!")
    return result
