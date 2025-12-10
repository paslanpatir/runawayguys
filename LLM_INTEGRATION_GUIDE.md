# LLM Integration Guide

## Available Free LLM Options

### 1. **Hugging Face Inference API** ⭐ Recommended
- **Free Tier**: 30,000 requests/month
- **Models**: Llama 2, Mistral, Mixtral, etc.
- **Setup**: Requires Hugging Face API token (free)
- **Pros**: 
  - Truly free with generous limits
  - Many open-source models
  - No credit card required
- **Cons**: 
  - Rate limits on free tier
  - Can be slower than paid services

### 2. **Groq** ⭐ Recommended (Very Fast)
- **Free Tier**: Generous free tier
- **Models**: Llama 3, Mixtral, Gemma
- **Setup**: Requires API key (free)
- **Pros**:
  - Extremely fast inference
  - Good free tier
  - Multiple model options
- **Cons**:
  - Requires account creation
  - Rate limits

### 3. **Ollama** (Local - Completely Free)
- **Free**: 100% free, runs locally
- **Models**: Llama 2, Mistral, CodeLlama, etc.
- **Setup**: Install Ollama locally
- **Pros**:
  - Completely free, no API limits
  - Runs on your machine
  - Privacy-focused
- **Cons**:
  - Requires local installation
  - Needs good hardware (GPU recommended)
  - Not suitable for production deployment

### 4. **Together AI** (Free Tier)
- **Free Tier**: $25 free credits
- **Models**: Llama 2, Mistral, Mixtral
- **Setup**: Requires API key
- **Pros**:
  - Good free credits
  - Multiple models
- **Cons**:
  - Requires credit card (but free tier available)

## Recommended Approach

For this project, I recommend **Hugging Face Inference API** or **Groq** because:
1. Truly free (no credit card needed for HF)
2. Easy to integrate
3. Good performance
4. Suitable for production

## Setup Instructions

### Option 1: Hugging Face (Recommended)

1. Go to https://huggingface.co/
2. Create free account
3. Go to Settings → Access Tokens
4. Create new token (read permission is enough)
5. Add to environment variable or config file:
   ```bash
   # Environment variable
   export HF_API_TOKEN="your_token_here"
   
   # Or in config/llm_credentials.txt:
   huggingface
   your_token_here
   mistralai/Mistral-7B-Instruct-v0.2
   ```

### Option 2: Groq (Very Fast)

1. Go to https://console.groq.com/
2. Create free account
3. Get API key from dashboard
4. Install package: `pip install groq`
5. Add to environment variable or config file:
   ```bash
   # Environment variable
   export GROQ_API_KEY="your_key_here"
   
   # Or in config/llm_credentials.txt:
   groq
   your_key_here
   llama-3.1-8b-instant
   ```

## Configuration File Format

Create `config/llm_credentials.txt`:
```
# Provider: huggingface or groq
huggingface
# API Key
your_api_key_here
# Model name (optional, defaults provided)
mistralai/Mistral-7B-Instruct-v0.2
```

## Features

- ✅ Generates personalized insights based on survey results
- ✅ Supports both Turkish and English
- ✅ Displays insights on results page
- ✅ Includes insights in email report
- ✅ Gracefully handles missing API keys (shows message instead of error)
