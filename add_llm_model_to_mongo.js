// MongoDB script to add LLM model
// Run this in MongoDB or use a MongoDB client

db.model.insertOne({
  "modelId": "gpt-neox-20b-model",
  "version": "1.0",
  "submittedOn": 1730000000,
  "updatedOn": 1730000000,
  "name": "GPT-NeoX 20B",
  "description": "GPT-NeoX 20B large language model for text generation",
  "refUrl": "https://github.com/EleutherAI/gpt-neox",
  "task": {
    "type": "text-generation"
  },
  "languages": [
    {"sourceLanguage": "en", "targetLanguage": null}
  ],
  "license": "Apache-2.0",
  "domain": ["general", "code", "summarization"],
  "inferenceEndPoint": {
    "task": "text-generation",
    "endpointURL": "http://13.203.154.110:9000/pipeline",
    "schema": {
      "request": {
        "type": "object",
        "properties": {
          "input": {
            "type": "array",
            "items": {"type": "string"}
          },
          "temperature": {"type": "number"},
          "max_tokens": {"type": "number"}
        }
      },
      "response": {
        "type": "object",
        "properties": {
          "output": {
            "type": "array",
            "items": {"type": "string"}
          }
        }
      }
    }
  },
  "benchmarks": [],
  "submitter": {
    "name": "AI4Bharat",
    "email": "contact@ai4bharat.org",
    "oauthId": null
  }
});

