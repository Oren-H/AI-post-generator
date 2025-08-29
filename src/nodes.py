from langchain_core.messages import SystemMessage, HumanMessage
from schemas import State
from langchain_openai import ChatOpenAI
from schemas import Quotes
from os import getenv

def _get_chat_model():
    # Lazily construct the client so that importing this module doesn't require OPENAI_API_KEY.
    return ChatOpenAI(model="gpt-4o", temperature=0)

pullout_sys_msg = SystemMessage("""You are a helpful assistant that generates article pull-out quotes. 
Each pull out quote should be 30-70 words and should capture the main themes of the article. 
The pull out quotes MUST be direct quotations from the article. 
DO NOT summarize or otherwise modify the direct quotations in any way. A quote can be 1-3 sentences long.""")

summarizer_sys_msg = SystemMessage("""You are a helpful assistant for the Columbia Sundial, a student publication. Your task is to summarize the article provided by the user. 
                        A summary should be 2-3 paragraphs and should capture all the main themes of the article. 
                        Note that some articles are op-eds and others are informative""")

insta_caption_sys_msg = SystemMessage("""You are a helpful assistant for the Columbia Sundial, a student publication. Your task is to generate a caption for an instagram post advertising one of Sundial's articles.
                           The caption should be 80-250 words, split into multiple lines and paragrpahs. 
                           Use a summary of the article and a list of a few relevant quotes from the article to help you generate a good caption.
                           Do not use hashtags or emojis in the caption.""")

def quote_generator(state: State):
    article = state["article"]
    chat = _get_chat_model()
    quote_llm = chat.with_structured_output(Quotes)
    return {"quotes": quote_llm.invoke([pullout_sys_msg, HumanMessage(content=article)])}

def summarizer(state: State):
    article = state["article"]
    chat = _get_chat_model()
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
    
