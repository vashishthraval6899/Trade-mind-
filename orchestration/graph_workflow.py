from typing import TypedDict, Optional, Dict, Any, List
from langgraph.graph import StateGraph

from retrieval.retrieve import retrieve
from ingestion.news_ingest import fetch_news
from agents.agents import bull_agent, bear_agent, judge_agent


SECTOR_MAP = {
    "TCS": "IT",
    "INFY": "IT",
    "HCLTECH": "IT",
    "HDFCBANK": "Banking",
    "ICICIBANK": "Banking",
    "SBIN": "Banking"
}


class TradeMindState(TypedDict):
    ticker: str
    sector: str
    evidence: str
    news: List[Dict[str, str]]
    bull: Optional[Dict[str, Any]]
    bear: Optional[Dict[str, Any]]
    final_score: Optional[int]
    score_label: Optional[str]
    judge: Optional[Dict[str, Any]]
    result: Optional[Dict[str, Any]]


# ----------------------------
# Retrieve
# ----------------------------
def retrieve_node(state: TradeMindState):
    ticker = state["ticker"]
    sector = SECTOR_MAP[ticker]

    macro_context = retrieve(
        query="interest rates inflation GDP liquidity outlook monetary policy",
        space="macro",
        top_k=3
    )

    sector_context = retrieve(
        query=f"{sector} sector outlook growth risks regulation demand",
        sector=sector,
        space="sector",
        top_k=3
    )

    company_context = retrieve(
        query=f"{ticker} earnings performance guidance risks outlook",
        ticker=ticker,
        space="company",
        top_k=3
    )

    combined_text = ""

    for group in [macro_context, sector_context, company_context]:
        for item in group:
            combined_text += item["text"][:350] + "\n\n"

    news_articles = fetch_news(ticker)

    for article in news_articles[:5]:
        combined_text += article["title"] + "\n"
        combined_text += article["summary"][:200] + "\n\n"


    return {
        "sector": sector,
        "evidence": combined_text,
        "news": news_articles[:5]
    }


# ----------------------------
# Bull Agent
# ----------------------------
def bull_node(state: TradeMindState):
    return {
        "bull": bull_agent(state["evidence"])
    }


# ----------------------------
# Bear Agent
# ----------------------------
def bear_node(state: TradeMindState):
    return {
        "bear": bear_agent(state["evidence"])
    }


# ----------------------------
# Join (Synchronization Barrier)
# ----------------------------
def join_node(state: TradeMindState):
    return {}


# ----------------------------
# Score
# ----------------------------
def score_node(state: TradeMindState):
    bull_score = state["bull"].get("bull_score", 50)
    bear_score = state["bear"].get("bear_score", 50)

    final_score = bull_score - bear_score

    if final_score >= 25:
        score_label = "BUY"
    elif final_score <= -25:
        score_label = "SELL"
    elif -10 <= final_score <= 10:
        score_label = "HOLD"
    elif final_score > 10:
        score_label = "BUY"
    else:
        score_label = "SELL"

    return {
        "final_score": final_score,
        "score_label": score_label
    }


# ----------------------------
# Judge
# ----------------------------
def judge_node(state: TradeMindState):
    return {
        "judge": judge_agent(
            bull_output=state["bull"],
            bear_output=state["bear"],
            score_label=state["score_label"],
            final_score=state["final_score"]
        )
    }


# ----------------------------
# Result
# ----------------------------
def result_node(state: TradeMindState):
    return {
        "result": {
            "ticker": state["ticker"],
            "sector": state["sector"],
            "metrics": {
                "bull_score": state["bull"].get("bull_score"),
                "bear_score": state["bear"].get("bear_score"),
                "final_score": state["final_score"]
            },
            "bull_summary": state["bull"].get("bull_summary"),
            "bear_summary": state["bear"].get("bear_summary"),
            "final_decision": state["judge"].get("final_decision"),
            "confidence": state["judge"].get("confidence"),
            "final_summary": state["judge"].get("final_summary"),
            "recent_news": state["news"]
        }
    }


# ----------------------------
# Build Graph
# ----------------------------
def build_graph():
    workflow = StateGraph(TradeMindState)

    # Nodes
    workflow.add_node("retrieve_node", retrieve_node)
    workflow.add_node("bull_agent_node", bull_node)
    workflow.add_node("bear_agent_node", bear_node)
    workflow.add_node("join_node", join_node)
    workflow.add_node("score_node", score_node)
    workflow.add_node("judge_node", judge_node)
    workflow.add_node("result_node", result_node)

    # Entry point
    workflow.set_entry_point("retrieve_node")

    # -----------------------------------
    # CONDITIONAL PARALLEL BRANCH
    # -----------------------------------

    def route_after_retrieve(state):
        return ["bull_agent_node", "bear_agent_node"]

    workflow.add_conditional_edges(
        "retrieve_node",
        route_after_retrieve,
        {
            "bull_agent_node": "bull_agent_node",
            "bear_agent_node": "bear_agent_node"
        },
    )

    # Join barrier
    workflow.add_edge("bull_agent_node", "join_node")
    workflow.add_edge("bear_agent_node", "join_node")

    workflow.add_edge("join_node", "score_node")
    workflow.add_edge("score_node", "judge_node")
    workflow.add_edge("judge_node", "result_node")

    workflow.set_finish_point("result_node")

    return workflow.compile()
