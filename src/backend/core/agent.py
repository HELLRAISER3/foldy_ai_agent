from typing import TypedDict, Sequence, Annotated

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from loguru import logger

from pathlib import Path

from src.backend.tools.tools import tools
from src.backend.utils.common import read_yaml
from src.backend.entities import *

import asyncio


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    root_folder: Path

class FoldyAgent():
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url="http://localhost:8000/v1",
            api_key="not-needed",
            temperature= 0,
            streaming=True
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", read_yaml(SYSTEM_PROMPT_PATH)["system_prompt"]),
            ("placeholder", "{messages}") 
        ])
        self.chain = (
            {
                "messages": lambda x: x["messages"]
            }
            | self.prompt
            | self.llm.bind_tools(tools=tools, tool_choice = "auto")
        )
        self.graph = self._compose_graph()

    async def _call_model(self, state: AgentState, config: RunnableConfig) -> dict:
        """Node that invokes the agent asynchronously."""
        response = self.chain.ainvoke({"messages": state["messages"]}, config)
        return {"messages": [response]}

    def _should_continue(self, state: AgentState):
        last_message = state["messages"][-1]
        if not last_message.tool_calls:
            return END
        return "tools"

    def _compose_graph(self):
        graph = StateGraph(AgentState)

        graph.add_node("call_model", self._call_model)
        graph.add_node("tools", ToolNode(tools))

        graph.set_entry_point("call_model")

        graph.add_conditional_edges(
            "call_model",
            self._should_continue
        )
        
        graph.add_edge("tools", "call_model")

        return graph.compile()
