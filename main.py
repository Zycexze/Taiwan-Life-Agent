from langchain_core.messages import HumanMessage

from agent.graph import build_agent

def main():
    agent = build_agent()

    config = {
        "configurable": {
            "thread_id": "taiwan-life-agent"
        }
    }

    print("AI：你好，我是臺灣生活助理。")
    print("AI：你可以問我天氣、警特報、附近餐廳、停車場、咖啡廳等問題。")
    print("AI：輸入 exit 可以結束。")

    while True:
        question = input("\n你：").strip()

        if question.lower() in {"exit", "quit", "q"}:
            print("AI：再見！")
            break

        if not question:
            continue

        result = agent.invoke(
            {
                "messages": [
                    HumanMessage(content=question)
                ]
            },
            config=config,
        )

        answer = result["messages"][-1].content

        if isinstance(answer, list):
            answer = "\n".join(
                str(item.get("text", item)) if isinstance(item, dict) else str(item)
                for item in answer
            )

        if not str(answer).strip():
            answer = "我已經查詢工具，但沒有產生文字回覆，請再問一次。"

        print(f"\nAI：{answer}")

if __name__ == "__main__":
    main()