import json
import re
from src.database import SessionLocal, get_last_n_days, QuestionLog
from src.analyzer import llm
from src.rag_engine import get_retriever

def ask_goldpulse(question, session_id=None):
    session = SessionLocal()
    rows = get_last_n_days(session, 30)

    if not rows:
        return {"error": "No gold price data available."}

    latest = rows[0]
    avg_24k = sum(row.price_24k for row in rows) / len(rows)
    avg_22k = sum(row.price_22k for row in rows) / len(rows)

    # --- 1. RAG KNOWLEDGE RETRIEVAL ---
    retriever = get_retriever()
    rag_context = "No historical context available."
    
    if retriever:
        try:
            docs = retriever.invoke(question)
            rag_context = "\n\n".join([doc.page_content for doc in docs])
        except Exception as e:
            print(f"RAG Error: {e}")

    # --- 2. CHAT MEMORY RETRIEVAL ---
    chat_memory = ""
    if session_id:
        past_turns = (
            session.query(QuestionLog)
            .filter_by(session_id=session_id)
            .order_by(QuestionLog.id.desc())
            .limit(3)
            .all()
        )
        for turn in reversed(past_turns):
            try:
                ans_json = json.loads(turn.answer)
                summary_text = ans_json.get("Market Summary", turn.answer)
            except:
                summary_text = turn.answer
            chat_memory += f"User: {turn.question}\nAssistant: {summary_text}\n"

    # --- 3. CONTEXT & PROMPT ---
    context = f"""
    Current 24K Price: {latest.price_24k}
    Current 22K Price: {latest.price_22k}
    30 Day Average 24K Price: {avg_24k:.2f}
    30 Day Average 22K Price: {avg_22k:.2f}
    
    Relevant Knowledge Base & Historical Reports (RAG):
    {rag_context}
    """

    prompt = f"""
    You are GoldPulse AI, an expert gold market assistant.
    Use the provided current data, the RAG knowledge base context, and recent conversation history to answer the user contextually.
    If the question is unrelated to gold, politely refuse.

    DATA:
    {context}

    RECENT CONVERSATION HISTORY (Use this to understand follow-up questions):
    {chat_memory}

    QUESTION:
    {question}

    OUTPUT INSTRUCTIONS:
    You must respond with ONLY a valid JSON object. No preamble, no postscript, no formatting ticks.
    The JSON must have EXACTLY these keys:
    "Market Summary": "A 2-3 sentence overview utilizing the RAG context."
    "Key Insights": "A single string containing a bulleted list of insights (use standard hyphens for bullets). DO NOT return an array."
    "Recommendation": "Buy, Sell, Hold, or Wait with a brief reason."
    "Risk Level": "Low, Medium, or High."
    "Confidence Score": "A percentage (e.g., 85%)."
    """

    response = llm.invoke(prompt).content

    try:
        # 1. Strip markdown ticks if the AI still included them
        cleaned_response = response.replace("```json", "").replace("```", "").strip()
        
        # 2. Extract ONLY the JSON dictionary using Regex (Ignores AI conversational text)
        match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
        if match:
            cleaned_response = match.group(0)

        parsed_json = json.loads(cleaned_response)
        
        # 3. Clean up lists (If the AI ignored instructions and returned an array for Key Insights)
        if isinstance(parsed_json.get("Key Insights"), list):
            parsed_json["Key Insights"] = "\n".join([f"• {item}" for item in parsed_json["Key Insights"]])
        
        # Save this interaction into the database history log
        log_entry = QuestionLog(
            session_id=session_id,
            question=question,
            answer=json.dumps(parsed_json)
        )
        session.add(log_entry)
        session.commit()
        
        return parsed_json
        
    except json.JSONDecodeError:
        # 4. Ultimate Fallback: If it completely fails, return safe UI data instead of a red code dump
        safe_error = {
            "Market Summary": "The AI encountered an issue structuring its response. Please try asking your question again.",
            "Key Insights": "Data parsing error. The requested insight was too complex to format.",
            "Recommendation": "Wait",
            "Risk Level": "Medium",
            "Confidence Score": "0%"}
        return safe_error


def stream_goldpulse(question, session_id=None):
    session = SessionLocal()
    rows = get_last_n_days(session, 30)

    if not rows:
        yield "Error: No gold price data available."
        return

    latest = rows[0]
    avg_24k = sum(row.price_24k for row in rows) / len(rows)
    avg_22k = sum(row.price_22k for row in rows) / len(rows)

    # --- 1. RAG KNOWLEDGE RETRIEVAL ---
    retriever = get_retriever()
    rag_context = "No historical context available."
    
    if retriever:
        try:
            docs = retriever.invoke(question)
            rag_context = "\n\n".join([doc.page_content for doc in docs])
        except Exception as e:
            print(f"RAG Error: {e}")

    # --- 2. CHAT MEMORY RETRIEVAL ---
    chat_memory = ""
    if session_id:
        past_turns = (
            session.query(QuestionLog)
            .filter_by(session_id=session_id)
            .order_by(QuestionLog.id.desc())
            .limit(5)
            .all()
        )
        for turn in reversed(past_turns):
            chat_memory += f"User: {turn.question}\nAssistant: {turn.answer}\n\n"

    # --- 3. CONTEXT & PROMPT ---
    context = f"""
    Current 24K Price: {latest.price_24k}
    Current 22K Price: {latest.price_22k}
    30 Day Average 24K Price: {avg_24k:.2f}
    30 Day Average 22K Price: {avg_22k:.2f}
    
    Relevant Knowledge Base & Historical Reports (RAG):
    {rag_context}
    """

    prompt = f"""
    You are GoldPulse AI, an expert gold market assistant.
    Use the provided current data, the RAG knowledge base context, and recent conversation history to answer the user contextually.
    If the question is unrelated to gold, politely refuse.

    DATA:
    {context}

    RECENT CONVERSATION HISTORY:
    {chat_memory}

    QUESTION:
    {question}

    OUTPUT INSTRUCTIONS:
    Respond directly to the user in a helpful, professional, and conversational tone using Markdown.
    Where applicable, structure your response with clear headers (e.g., ### Market Summary, ### Key Insights, ### Recommendation, ### Risk, ### Confidence) so the user can easily parse structured financial data.
    """

    full_response = ""
    try:
        for chunk in llm.stream(prompt):
            text = chunk.content
            full_response += text
            yield text
            
        # Only save if the stream completes successfully (no interruption)
        if session_id:
            log_entry = QuestionLog(
                session_id=session_id,
                question=question,
                answer=full_response
            )
            session.add(log_entry)
            session.commit()
            
    except GeneratorExit:
        # Client disconnected prematurely. Do not save partial response.
        pass
    except Exception as e:
        print(f"Streaming Error: {e}")
        yield "\n\n**An error occurred while generating the response.**"
    finally:
        session.close()