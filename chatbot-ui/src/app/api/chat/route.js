import { GoogleGenAI } from '@google/genai';
import fs from 'fs';
import path from 'path';

export async function POST(request) {
  try {
    const { messages } = await request.json();

    // Read the sanitized history file
    const dataFilePath = path.join(process.cwd(), 'src/data/subset_10k_sanitized.txt');
    const historyText = fs.readFileSync(dataFilePath, 'utf8');

    // Initialize the Gemini client
    const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
    
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
