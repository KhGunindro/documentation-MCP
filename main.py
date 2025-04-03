from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import json
import os
import httpx

load_dotenv()

mcp = FastMCP("docs")

USER_AGENT = "docs-app/1.0"
SERPER_URL = "https://google.serper.dev/search"

docs_urls = {
    "react" : "https://react.dev/learn",
    "vite" : "https://vuejs.org/guide/introduction",
    "tailwind" : "https://tailwindcss.com/docs/installation/using-vite",
    "shadcn" : "https://ui.shadcn.com/docs/installation"
}   

# 1
async def search_web(query: str) -> dict | None:
   payload = json.dumps({"q":query, "num":2})

   headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json",
   }

   async with httpx.AsyncClient() as client:
        try: 
           response = await client.post(
               SERPER_URL, headers=headers, data=payload, timeout=30.0
           )
           response.raise_for_status()
           return response.json()
        except httpx.TimeoutException:
           return {"organic": []}    


# 2
async def fetch_url(url: str):
    async with httpx.AsyncClient() as Client:
        try: 
            response = await Client.get(url, timeout=30.0)
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()
            return text
        except httpx.TimeoutException:
            return "Timeout error"

# This will convert the function definition to a tool which the mcp server can use
@mcp.tool()
async def get_docs(query: str, library: str):
    """
    Get the lastests documentation for a given library and query.
    Supports react, vue, angular, tailwind and shadcn.

    Args:
        query (str): The query to search for. (e.g "installation")
        library (str): The library to search for. (e.g "react")
    
    Returns:
        lists of dictionaries that contains source URLs and extracted text
    """
    if library not in docs_urls:
        raise ValueError(f"Library {library} not supported. Supported libraries are: {', '.join(docs_urls.keys())}")
    
    query = f"site:{docs_urls[library]} {query}"
    results = await search_web(query)
    if len(results["organic"]) == 1:
        return "No results found"
    
    # text = ""
    # for result in results["organic"]:
    #     text += await fetch_url(result["link"])
    #     return text
    


def main():
    print("Hello from documentation!")


if __name__ == "__main__":
    mcp.run(transport='stdio')