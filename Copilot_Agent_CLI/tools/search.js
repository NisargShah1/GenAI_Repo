/**
 * Search the web using Google Custom Search API.
 * This tool allows the Copilot Agent to search the internet for documentation, 
 * solutions, or external context required during the development loop.
 * 
 * Keys are dynamically loaded from ~/.copilot-agent-secrets.json or process.env
 */
export async function googleSearch(query, numResults = 5) {
  // `ensureSecrets` from config.js already injects these into process.env 
  const apiKey = process.env.GOOGLE_API_KEY;
  const cx = process.env.GOOGLE_SEARCH_ENGINE_ID;
  
  if (!apiKey || !cx) {
    console.warn("⚠️ Warning: GOOGLE_API_KEY or GOOGLE_SEARCH_ENGINE_ID is missing from local secrets. Running in mock mode.");
    return [
      {
        title: `Mock Result for: ${query}`,
        link: "https://example.com",
        snippet: "This is a mock search result because API keys were not provided in ~/.copilot-agent-secrets.json."
      }
    ];
  }

  const url = `https://www.googleapis.com/customsearch/v1?q=${encodeURIComponent(query)}&key=${apiKey}&cx=${cx}&num=${numResults}`;
  
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Google Search API failed with status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.items.map(item => ({
      title: item.title,
      link: item.link,
      snippet: item.snippet
    }));
  } catch (error) {
    console.error("Error executing Google Search:", error.message);
    throw error;
  }
}
