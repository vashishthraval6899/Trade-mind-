from orchestration.graph_workflow import build_graph

graph = build_graph()

def analyze(ticker: str):
    state = graph.invoke({
        "ticker": ticker.upper(),
        "sector": "",
        "evidence": "",
        "news": [],
        "bull": None,
        "bear": None,
        "final_score": None,
        "score_label": None,
        "judge": None,
        "result": None
    })

    return state["result"]
