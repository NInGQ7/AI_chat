from tavily import TavilyClient
from app.services.skill_manager import skill_registry, SkillContext
from app.core.config import settings

@skill_registry.register("tavily_search", "Search web. Args: query")
def tavily_search(query: str, context: SkillContext):
    if not settings.TAVILY_API_KEY:
        return "Error: Tavily API Key not configured."
        
    client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    response = client.search(query=query, search_depth="basic")
    
    results = [f"[{r['title']}]({r['url']}): {r['content'][:200]}..." for r in response.get('results', [])[:3]]
    return "\n".join(results)