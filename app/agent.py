from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END

from app.data_loader import load_financial_data
from app.anomaly_detector import detect_amount_anomalies
from app.llm_service import classify_financial_query


class AgentState(TypedDict):
    question: str
    intent: str
    answer: str
    results: list


def classify_node(state: AgentState) -> AgentState:
    question = state["question"]
    classification = classify_financial_query(question)
    intent = classification.get("intent", "unknown")

    return {
        **state,
        "intent": intent,
    }


def execute_node(state: AgentState) -> AgentState:
    question = state["question"]
    intent = state["intent"]
    df = load_financial_data()

    if intent == "detect_anomalies":
        anomalies = detect_amount_anomalies(df)
        return {
            **state,
            "answer": "Here are the invoices flagged as anomalous based on unusually high amounts.",
            "results": anomalies,
        }

    if intent == "list_invoices":
        return {
            **state,
            "answer": "Here are all invoices in the dataset.",
            "results": df.to_dict(orient="records"),
        }

    if intent == "health_check":
        return {
            **state,
            "answer": "The AI Financial Agent is running normally.",
            "results": [{"status": "ok"}],
        }

    return {
        **state,
        "answer": (
            "I could not understand that request yet. "
            "Try asking things like 'show suspicious invoices' or 'list all invoices'."
        ),
        "results": [],
    }


def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("classify", classify_node)
    graph.add_node("execute", execute_node)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "execute")
    graph.add_edge("execute", END)

    return graph.compile()


financial_agent = build_agent()


def run_financial_agent(question: str) -> Dict[str, Any]:
    result = financial_agent.invoke(
        {
            "question": question,
            "intent": "",
            "answer": "",
            "results": [],
        }
    )

    return {
        "question": result["question"],
        "intent": result["intent"],
        "answer": result["answer"],
        "results": result["results"],
    }