"""
RAG Chain: Combines vector retrieval with LLM generation.
Gracefully degrades when OpenAI API key is not configured.
"""

from typing import List, Tuple
from config import settings
from rag.vector_store import similarity_search


SYSTEM_PROMPT = """You are an intelligent AI News Assistant. 
Answer questions about news and current events based on the articles provided.
Be concise, factual, and helpful."""


async def get_rag_answer(
    query: str,
    user_preferences: List[str] = None,
    chat_history: List[Tuple[str, str]] = None,
) -> dict:
    """
    RAG pipeline: retrieve relevant docs → generate answer with LLM.
    Falls back to a simple summary when OpenAI is not configured.
    """

    # Retrieve relevant documents from FAISS
    relevant_docs = similarity_search(query, k=5)
    sources = []
    context_text = ""

    if relevant_docs:
        parts = []
        for doc in relevant_docs:
            parts.append(
                f"Title: {doc.metadata.get('title', '')}\n"
                f"Source: {doc.metadata.get('source', '')}\n"
                f"Content: {doc.page_content[:400]}"
            )
            url = doc.metadata.get("url", "")
            if url and url not in sources:
                sources.append(url)
        context_text = "\n\n---\n\n".join(parts)

    # No OpenAI key — return a helpful fallback answer
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("sk-your"):
        if relevant_docs:
            titles = [d.metadata.get("title", "") for d in relevant_docs[:3]]
            answer = (
                f"🔍 I found {len(relevant_docs)} relevant articles for **\"{query}\"**:\n\n"
                + "\n".join(f"• {t}" for t in titles)
                + "\n\n> ⚠️ AI answers require an OpenAI API key. "
                "Add `OPENAI_API_KEY` to `backend/.env` to enable full AI responses."
            )
        else:
            answer = (
                f"I searched for **\"{query}\"** but found no matching articles yet.\n\n"
                "Try clicking **Refresh Feed** on the home page first, then ask again.\n\n"
                "> ⚠️ Full AI answers require an OpenAI API key in `backend/.env`."
            )
        return {"answer": answer, "sources": sources}

    # Full RAG with OpenAI
    try:
        from langchain_openai import ChatOpenAI
        from langchain.agents import AgentExecutor, create_openai_tools_agent
        from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain.schema import HumanMessage, AIMessage
        from mcp_tools.tools import create_mcp_tools

        enhanced_query = query
        if context_text:
            enhanced_query = (
                f"Based on these news articles:\n\n{context_text}\n\n"
                f"Answer: {query}"
            )
        if user_preferences:
            enhanced_query += f"\n\n(User interests: {', '.join(user_preferences)})"

        llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model="gpt-3.5-turbo",
            temperature=0.3,
        )
        tools = create_mcp_tools()
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(llm, tools, prompt)
        executor = AgentExecutor(
            agent=agent, tools=tools, verbose=False,
            max_iterations=3, handle_parsing_errors=True,
        )

        history_messages = []
        if chat_history:
            for human_msg, ai_msg in chat_history[-3:]:
                history_messages.append(HumanMessage(content=human_msg))
                history_messages.append(AIMessage(content=ai_msg))

        result = await executor.ainvoke({
            "input": enhanced_query,
            "chat_history": history_messages,
        })
        return {"answer": result.get("output", "No answer generated."), "sources": sources}

    except Exception as e:
        print(f"RAG error: {e}")
        # Fallback: direct LLM call
        try:
            from langchain_openai import ChatOpenAI
            from langchain.schema import HumanMessage, SystemMessage
            llm = ChatOpenAI(openai_api_key=settings.OPENAI_API_KEY, model="gpt-3.5-turbo", temperature=0.3)
            msgs = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=query)]
            if context_text:
                msgs.insert(1, HumanMessage(content=f"Context:\n{context_text}"))
            resp = await llm.ainvoke(msgs)
            return {"answer": resp.content, "sources": sources}
        except Exception as e2:
            return {"answer": f"Error: {str(e2)}", "sources": []}
