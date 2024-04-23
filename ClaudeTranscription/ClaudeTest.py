import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="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",
)
message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    temperature=0,
    system="Today is March 4, 2024.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What are 3 ways to cook apples?"
                }
            ]
        }
    ]
)
print(message.content)