import asyncio
import typer
from pathlib import Path
from src.backend.core.agent import FoldyAgent
from langchain_core.messages import HumanMessage
from src.cli.display import ConsoleDisplay 
from loguru import logger
app = typer.Typer(help="Foldy AI: Your local filesystem manager.")
display = ConsoleDisplay()

@app.command()
def do(instruction: str):
    """Tell Foldy what to do with your files."""
    agent = FoldyAgent()
    
    async def run():
        current_working_dir = Path.cwd()
        
        inputs = {
            "messages": [HumanMessage(content=instruction)],
            "root_folder": current_working_dir
        }
        
        display.print_startup(current_working_dir)

        async for event in agent.graph.astream_events(inputs, version="v2"):
            kind = event["event"]
            # logger.info(f"current event: {event}")
            if kind == "on_chat_model_stream":
                display.stream_token(event["data"]["chunk"].content)
            
            elif kind == "on_tool_start":
                display.print_tool_call(event["name"], event["data"].get("input"))
                
            elif kind == "on_tool_end":
                display.print_tool_result(event["data"].get("output"))

    asyncio.run(run())

if __name__ == "__main__":
    app()