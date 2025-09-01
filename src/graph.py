from langgraph.graph import START, END, StateGraph
from .nodes import quote_generator, summarizer, insta_caption_generator
from .schemas import State


class Graph:
    def __init__(self):
        builder = StateGraph(State)

        # Nodes
        builder.add_node("quote_generator", quote_generator)
        builder.add_node("summarizer", summarizer)
        builder.add_node("insta_caption_generator", insta_caption_generator)

        # Edges
        builder.add_edge(START, "quote_generator")
        builder.add_edge(START, "summarizer")
        builder.add_edge("summarizer", "insta_caption_generator")
        builder.add_edge("quote_generator", "insta_caption_generator")
        builder.add_edge("insta_caption_generator", END)

        self.graph = builder.compile()

    def invoke(self, state, config=None):
        return self.graph.invoke(state, config=config)
