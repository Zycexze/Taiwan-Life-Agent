from typing import Annotated, TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from agent.prompts import SYSTEM_PROMPT
from agent.tools import TOOLS
from agent.memory import get_memory
from config import GEMINI_API_KEY

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    retry_count: int


llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=GEMINI_API_KEY,
    temperature=0,
)

llm_with_tools = llm.bind_tools(TOOLS)


def is_tool_failed(text: str) -> bool:
    fail_keywords = [
        "找不到",
        "查無",
        "沒有結果",
        "不支援",
        "無法定位",
        "定位失敗",
        "查詢失敗",
        "API 連線失敗",
        "資料解析失敗",
    ]
    return any(keyword in text for keyword in fail_keywords)


def call_model(state: AgentState):
    messages = state["messages"]

    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response],
        "retry_count": state.get("retry_count", 0),
    }


def should_continue(state: AgentState):
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return END


def check_tool_result(state: AgentState):
    last_message = state["messages"][-1]
    retry_count = state.get("retry_count", 0)
    content = getattr(last_message, "content", "")

    if is_tool_failed(content) and retry_count < 2:
        retry_instruction = SystemMessage(
            content=(
                "剛才工具查詢失敗。請自行判斷是否可能是地名錯字、簡稱、"
                "台/臺差異、地點過於模糊或類別不精確。"
                "請修正查詢參數後，再重新呼叫工具一次。"
                "不要直接回答失敗。"
            )
        )

        return {
            "messages": [retry_instruction],
            "retry_count": retry_count + 1,
        }

    return {
        "retry_count": retry_count,
    }


def build_agent():
    tool_node = ToolNode(TOOLS)

    workflow = StateGraph(AgentState)

    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.add_node("check_tool_result", check_tool_result)

    workflow.add_edge(START, "agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )

    workflow.add_edge("tools", "check_tool_result")
    workflow.add_edge("check_tool_result", "agent")

    graph = workflow.compile(
        checkpointer=get_memory()
    )

    return graph