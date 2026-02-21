from __future__ import annotations

import json
import streamlit as st

from multi_agent_pipeline.agents import (
    RequirementsAgent,
    InceptionAgent,
    UserStoriesAgent,
    ERDesignAgent,
)
from multi_agent_pipeline.llm import GroqJSONClient


AGENT_ORDER = ["requirements", "inception", "user_stories", "er_design"]

AGENT_LABELS = {
    "requirements": "1. Requirements Agent",
    "inception": "2. Inception Agent",
    "user_stories": "3. User Stories Agent",
    "er_design": "4. ER Design Agent",
}


def run_single_agent(agent_name: str, state: dict):
    llm = GroqJSONClient(model=state["model"])

    if agent_name == "requirements":
        agent = RequirementsAgent(llm)
        payload = {"brief": state["brief"]}

    elif agent_name == "inception":
        agent = InceptionAgent(llm)
        payload = {"brief": state["brief"], "requirements": state["outputs"]["requirements"]}
        # payload = state["outputs"]["requirements"]

    elif agent_name == "user_stories":
        agent = UserStoriesAgent(llm)
        # payload = {**state["outputs"]["inception"], **state["outputs"]["requirements"]}
        payload = {"brief": state["brief"], "requirements": state["outputs"]["requirements"], "inception": state["outputs"]["inception"]}

    elif agent_name == "er_design":
        agent = ERDesignAgent(llm)
        # payload = {**state["outputs"]["user_stories"], **state["outputs"]["inception"], **state["outputs"]["requirements"]}
        payload = {"brief": state["brief"], "requirements": state["outputs"]["requirements"], "inception": state["outputs"]["inception"], "user_stories": state["outputs"]["user_stories"]}

    else:
        return None

    return agent.run(payload).model_dump()


def main() -> None:
    st.set_page_config(page_title="Multi-Agent SE Pipeline")
    st.title("Multi-Agent SE Artifacts")
    st.caption("Submit a brief and review each agent output before continuing.")

    # ---- Initialize session state ----
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = {
            "current_agent": None,
            "outputs": {},
            "brief": None,
            "model": None,
            "running": False,
            "final": None,
        }

    # ---- Input Form ----
    with st.form("brief_form", clear_on_submit=False):
        brief_text = st.text_area(
            "Initial Brief",
            height=220,
            placeholder="Describe the product, users, goals, and constraints...",
        )
        model = st.text_input("Model", value="llama-3.1-8b-instant")
        run_clicked = st.form_submit_button("Run Pipeline", type="primary")

    # ---- Start Pipeline ----
    if run_clicked:
        if len(brief_text.strip()) < 50:
            st.error("Brief must be at least 50 characters.")
            return

        st.session_state.pipeline = {
            "current_agent": "requirements",
            "outputs": {},
            "brief": brief_text.strip(),
            "model": model.strip(),
            "running": True,
            "final": None,
        }

    state = st.session_state.pipeline

    # ---- HITL Execution Block ----
    if state["running"] and state["current_agent"]:
        agent_name = state["current_agent"]

        st.divider()
        st.subheader(AGENT_LABELS[agent_name])

        # Generate output if not yet generated
        if agent_name not in state["outputs"]:
            with st.spinner("Generating..."):
                output = run_single_agent(agent_name, state)
                state["outputs"][agent_name] = output
            st.rerun()

        output = state["outputs"][agent_name]
        st.json(output, expanded=True)

        col1, col2 = st.columns(2)

        # ---- Approve ----
        with col1:
            if st.button("✅ Approve", key=f"approve_{agent_name}"):
                idx = AGENT_ORDER.index(agent_name)

                if idx + 1 < len(AGENT_ORDER):
                    state["current_agent"] = AGENT_ORDER[idx + 1]
                else:
                    state["current_agent"] = None
                    state["running"] = False
                    state["final"] = state["outputs"]

                st.rerun()

        # ---- Reject ----
        with col2:
            if st.button("❌ Reject & Regenerate", key=f"reject_{agent_name}"):
                del state["outputs"][agent_name]
                st.rerun()

    # ---- Final Output ----
    if state["final"]:
        st.divider()
        st.subheader("Final Artifacts")
        st.json(state["final"], expanded=True)

        st.download_button(
            "Download final_artifacts.json",
            data=json.dumps(state["final"], indent=2),
            file_name="final_artifacts.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()