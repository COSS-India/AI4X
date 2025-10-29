// MongoDB script to add LLM service
// Run this in MongoDB or use a MongoDB client

db.service.insertOne({
  "serviceId": "ai-llm/gpt-neox-20b",
  "name": "GPT-NeoX 20B LLM Service",
  "serviceDescription": "Text generation using GPT-NeoX 20B model",
  "hardwareDescription": "GPU optimized for large language models",
  "publishedOn": 1730000000,
  "modelId": "gpt-neox-20b-model",
  "endpoint": "http://13.203.154.110:9000/pipeline", // Replace with actual endpoint
  "api_key": "your_service_api_key_here", // Generate a secure API key
  "healthStatus": null,
  "benchmarks": null
});

