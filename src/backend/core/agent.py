from typing import TypedDict, Sequence, Annotated

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
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
import json
import re

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    root_folder: Path

class FoldyAgent():
    def __init__(self):
        self.tools = tools

        self.llm = ChatOpenAI(
            base_url="http://localhost:8000/v1",
            api_key="not-needed",
            temperature= 0,
            streaming=True,
            name = "phi-4"
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
            | self.llm.bind_tools(tools=self.tools, tool_choice = "auto") # tool_choice = "required"
        )
        self.graph = self._compose_graph()

    async def _call_model(self, state: AgentState, config: RunnableConfig) -> dict:
        """Node that invokes the agent and handles hallucinated tool calls."""
    
        messages_for_llm = []
        for msg in state["messages"]:
            if isinstance(msg, ToolMessage):
                # We relabel the tool output so the model sees it clearly
                messages_for_llm.append(HumanMessage(
                    content=f"SYSTEM OBSERVATION (Tool: {msg.name}): {msg.content}"
                ))
            else:
                messages_for_llm.append(msg)
        # logger.info(f"messages_for_llm: {messages_for_llm}")

        response = await self.chain.ainvoke({"messages": messages_for_llm}, config)
        
        if not response.tool_calls:
            content = response.content.strip()

            content = content.replace("```json", "").replace("```", "")

            match = re.search(r'(\[\s*\{.*\}\s*\])', content, re.DOTALL)

            if match:
                json_str = match.group(1)

                try:
                    parsed_calls = json.loads(json_str)

                    if isinstance(parsed_calls, list):
                        response.tool_calls = [
                            {
                                "name": call.get("name"),
                                "args": call.get("args") or call.get("arguments") or {},
                                "id": f"call_{i}",
                                "type": "tool_call"
                            }
                            for i, call in enumerate(parsed_calls)
                        ]

                except Exception as e:
                    logger.debug(f"JSON extraction failed: {e}")

        return {"messages": [response]}

    def _should_continue(self, state: AgentState):
        last_message = state["messages"][-1]
        if not last_message.tool_calls:
            return END
        return "tools"
    
    def _compose_graph(self):
        graph = StateGraph(AgentState)

        graph.add_node("call_model", self._call_model)
        graph.add_node("tools", ToolNode(self.tools))

        graph.set_entry_point("call_model")

        graph.add_conditional_edges(
            "call_model",
            self._should_continue
        )
        
        graph.add_edge("tools", "call_model")

        return graph.compile()


