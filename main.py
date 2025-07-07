from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
import json
from tools import search_tool, wiki_tool

load_dotenv()

class ResearchResponse(BaseModel):
    topic : str
    summary: str
    sources: list[str]
    tools_used: list[str]
    
llm = ChatOpenAI(model="gpt-4o-mini")
parser = PydanticOutputParser(pydantic_object = ResearchResponse)

## Setup Prompt tempelate
prompt = ChatPromptTemplate.from_messages(
    
    [
        (
            "system",
            """ 
            You are a research assistant that will help generate a research paper.
            Answer the user query and use necessary tools.
            Wrap the output in this format and provide no other tet=xt \n{format_instructions}
            
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}")
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [search_tool, wiki_tool]

agent = create_tool_calling_agent(
    llm = llm,
    prompt = prompt,
    tools = tools
)

executor = AgentExecutor(agent = agent, tools = tools, verbose = True)
query = input("How can I help you with research? ")
raw_response = executor.invoke({"query": query})

output_str = raw_response.get("output")

try:
    structured_response = parser.parse(output_str)
except Exception as e:
    print(f"Error in {e}")