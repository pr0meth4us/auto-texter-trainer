import { GoogleGenAI } from '@google/genai';
import fs from 'fs';
import path from 'path';
import os from 'os';

let configCache = { value: null, expires: 0 };

async function getVertexAiCredentials() {
  if (Date.now() < configCache.expires && configCache.value?.GOOGLE_APPLICATION_CREDENTIALS_JSON) {
    return configCache.value.GOOGLE_APPLICATION_CREDENTIALS_JSON;
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
          return data.data.api_keys.GOOGLE_APPLICATION_CREDENTIALS_JSON;
        }
      } else {
        console.error('Failed to fetch from Bifrost:', res.status);
      }
    } catch (e) {
      console.error('Error fetching Bifrost config:', e);
    }
  } else {
    console.warn("Bifrost credentials missing.");
  }
  return process.env.GOOGLE_APPLICATION_CREDENTIALS_JSON;
}

export async function POST(request) {
  try {
    const { messages } = await request.json();

    // Read the sanitized history file
    const dataFilePath = path.join(process.cwd(), 'src/data/subset_10k_sanitized.txt');
    const historyText = fs.readFileSync(dataFilePath, 'utf8');

    const credsJson = await getVertexAiCredentials();
    if (!credsJson) {
      throw new Error("GOOGLE_APPLICATION_CREDENTIALS_JSON is not configured in Bifrost.");
    }

    // Write to a temporary file for the SDK to consume
    const tmpCredsPath = path.join(os.tmpdir(), 'bifrost_vertex_creds.json');
    fs.writeFileSync(tmpCredsPath, credsJson, 'utf8');
    process.env.GOOGLE_APPLICATION_CREDENTIALS = tmpCredsPath;

    // Initialize the Vertex AI client
    const ai = new GoogleGenAI({ 
        vertexai: { 
            project: 'khmer-ocr-496606', 
            location: 'asia-southeast1' 
        } 
    });
    
    // Construct system prompt
    const systemInstruction = [
        "You are a casual, bilingual Gen-Z Cambodian (Khmer) automated texting assistant.",
        "You are completely fluent in English, but you frequently mix in 'Latinized Khmer'.",
        "ALWAYS use all lowercase letters. Do not use punctuation like periods.",
        "Here is a history of my texting. Clone my exact personality perfectly:\n\n",
        historyText
    ].join('\n');

    // Format previous messages for the Gemini SDK
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
