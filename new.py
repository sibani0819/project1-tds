OpenAI API
GET /openai/*: Proxy requests to OpenAI

Example: List OpenAI models

curl https://aipipe.org/openai/v1/models -H "Authorization: Bearer $AIPIPE_TOKEN"
Response contains:

{
  "object": "list",
  "data": [
    {
      "id": "gpt-4o-audio-preview-2024-12-17",
      "object": "model",
      "created": 1734034239,
      "owned_by": "system",
    },
    // ...
  ],
}
Example: Make a responses request

curl https://aipipe.org/openai/v1/responses \
  -H "Authorization: Bearer $AIPIPE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4.1-nano", "input": "What is 2 + 2?" }'
Response contains:

{
  "output": [
    {
      "role": "assistant",
      "content": [{ "text": "2 + 2 equals 4." }],
      // ...
    },
  ],
}
Example: Create embeddings

curl https://aipipe.org/openai/v1/embeddings \
  -H "Authorization: Bearer $AIPIPE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model": "text-embedding-3-small", "input": "What is 2 + 2?" }'
Response contains:

{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [
        0.010576399, -0.037246477,
        // ...
      ],
    },
  ],
  "model": "text-embedding-3-small",
  "usage": {
    "prompt_tokens": 8,
    "total_tokens": 8,
  },
}