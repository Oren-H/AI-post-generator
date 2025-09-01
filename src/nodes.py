from langchain_core.messages import SystemMessage, HumanMessage
from .schemas import State
from langchain_openai import ChatOpenAI
from .schemas import Quotes
from .prompts import pullout_sys_msg, summarizer_sys_msg, insta_caption_sys_msg

def _get_chat_model(model = 'gpt-4o'):
    # Lazily construct the client so that importing this module doesn't require OPENAI_API_KEY.
    return ChatOpenAI(model=model, temperature=0)

def quote_generator(state: State):
    article = state["article"]
    chat = _get_chat_model()
    quote_llm = chat.with_structured_output(Quotes)
    return {"quotes": quote_llm.invoke([pullout_sys_msg, HumanMessage(content=article)])}

def summarizer(state: State):
    article = state["article"]
    chat = _get_chat_model(model="gpt-4o-mini")
    resp = chat.invoke([summarizer_sys_msg, HumanMessage(content=article)])
    # Extract text if model returns a message object
    summary_text = getattr(resp, "content", resp)
    return {"summary": summary_text}

def insta_caption_generator(state: State):
    summary = state["summary"]
    quotes = state["quotes"].quotes if hasattr(state["quotes"], "quotes") else state["quotes"]
    quotes_text = "\n\n".join(quotes)
    chat = _get_chat_model()
    resp = chat.invoke([
        insta_caption_sys_msg,
        HumanMessage(content=summary),
        HumanMessage(content=quotes_text),
    ])
    insta_caption_text = getattr(resp, "content", resp)
    return {"insta_caption": insta_caption_text}
    
