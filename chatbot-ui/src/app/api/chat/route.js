import { GoogleGenAI } from '@google/genai';
import fs from 'fs';
import path from 'path';

let configCache = { value: null, expires: 0 };

async function getGeminiApiKey() {
  if (Date.now() < configCache.expires && configCache.value?.GEMINI_API_KEY) {
    return configCache.value.GEMINI_API_KEY;
  }
  
  const url = (process.env.BIFROST_URL || "http://bifrost:5000").replace(/\/$/, "");
  const clientId = process.env.BIFROST_CLIENT_ID;
  const webhookSecret = process.env.BIFROST_WEBHOOK_SECRET;

  if (clientId && webhookSecret) {
    try {
      const res = await fetch(`${url}/api/v1/config`, {
        headers: {
          'X-Client-ID': clientId,
          'X-Webhook-Secret': webhookSecret
        }
      });
      if (res.ok) {
        const data = await res.json();
        if (data.status === 'success' && data.data && data.data.api_keys) {
          configCache = { value: data.data.api_keys, expires: Date.now() + 300000 }; // 5 min cache
          return data.data.api_keys.GEMINI_API_KEY || process.env.GEMINI_API_KEY;
        }
      } else {
        console.error('Failed to fetch from Bifrost:', res.status);
      }
    } catch (e) {
      console.error('Error fetching Bifrost config:', e);
    }
  } else {
    console.warn("Bifrost credentials missing, falling back to local env.");
  }
  return process.env.GEMINI_API_KEY;
}

export async function POST(request) {
  try {
    const { messages } = await request.json();

    // Read the sanitized history file
    const dataFilePath = path.join(process.cwd(), 'src/data/subset_10k_sanitized.txt');
    const historyText = fs.readFileSync(dataFilePath, 'utf8');

    const apiKey = await getGeminiApiKey();
    if (!apiKey) {
      throw new Error("GEMINI_API_KEY is not configured.");
    }

    // Initialize the Gemini client
    const ai = new GoogleGenAI({ apiKey });
    
    // Construct system prompt
    const systemInstruction = [
        "You are a casual, bilingual Gen-Z Cambodian (Khmer) automated texting assistant.",
        "You are completely fluent in English, but you frequently mix in 'Latinized Khmer'.",
        "ALWAYS use all lowercase letters. Do not use punctuation like periods.",
        "Here is a history of my texting. Clone my exact personality perfectly:\n\n",
        historyText
    ].join('\n');

    // Format previous messages for the Gemini SDK
    // Next.js client sends an array of { role: 'user' | 'assistant', content: string }
    const contents = messages.map(msg => ({
      role: msg.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: msg.content }]
    }));

    // Call the model
    const response = await ai.models.generateContent({
        model: 'gemini-3.5-flash',
        contents,
        config: {
            systemInstruction: systemInstruction,
            temperature: 0.8
        }
    });

    return new Response(JSON.stringify({ text: response.text }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('API Route Error:', error);
    return new Response(JSON.stringify({ error: error.message || 'An error occurred' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}
