/**
 * Search the web using Google Custom Search API.
 * This tool allows the Copilot Agent to search the internet for documentation, 
 * solutions, or external context required during the development loop.
 * 
 * Requires GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID (CX) environment variables.
 */
export async function googleSearch(query, numResults = 5) {
  const apiKey = process.env.GOOGLE_API_KEY;
  const cx = process.env.GOOGLE_SEARCH_ENGINE_ID;
  
  if (!apiKey || !cx) {
    console.warn("⚠️ Warning: GOOGLE_API_KEY or GOOGLE_SEARCH_ENGINE_ID is missing. Running in mock mode.");
    return [
      {
        title: `Mock Result for: ${query}`,
        link: "https://example.com",
        snippet: "This is a mock search result because API keys were not provided. Set GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID in your environment."
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
