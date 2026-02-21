from __future__ import annotations

from collections.abc import Callable
from typing import Optional

from pydantic import BaseModel

from .agents import ERDesignAgent, InceptionAgent, RequirementsAgent, TestCasesAgent, UserStoriesAgent
from .schemas import FinalArtifactsPackage, InitialBriefInput


def run_pipeline(
    brief_text: str,
    model: str | None = None,
    provider: str | None = None,
    on_agent_complete: Callable[[str, BaseModel], None] | None = None,
    on_requirements_ready: Optional[Callable[[BaseModel],bool]]=None,
) -> FinalArtifactsPackage:
    from .llm import get_llm_client
    initial = InitialBriefInput(brief_text=brief_text)
    llm = get_llm_client(provider=provider, model=model or "")

    req_agent = RequirementsAgent(llm)
    inc_agent = InceptionAgent(llm)
    us_agent = UserStoriesAgent(llm)
    er_agent = ERDesignAgent(llm)
    tc_agent = TestCasesAgent(llm)

    req = req_agent.run({"initial_brief": initial.model_dump()})
    if on_agent_complete:
        on_agent_complete("requirements", req)

    if on_requirements_ready:
        if not on_requirements_ready(req):
            print("Pipeline halted by on_requirements_ready callback.")
            
    inc = inc_agent.run(
        {
            "initial_brief": initial.model_dump(),
            "requirements": req.model_dump(),
        }
    )
    if on_agent_complete:
        on_agent_complete("inception", inc)

    stories = us_agent.run(
        {
            "initial_brief": initial.model_dump(),
            "requirements": req.model_dump(),
            "inception": inc.model_dump(),
        }
    )
    if on_agent_complete:
        on_agent_complete("user_stories", stories)

    test_cases = tc_agent.run(
        {
            "initial_brief": initial.model_dump(),
            "requirements": req.model_dump(),
            "inception": inc.model_dump(),
            "user_stories": stories.model_dump(),
        }
    )
    if on_agent_complete:
        on_agent_complete("test_cases", test_cases)

    er = er_agent.run(
        {
            "initial_brief": initial.model_dump(),
            "requirements": req.model_dump(),
            "inception": inc.model_dump(),
            "user_stories": stories.model_dump(),
            "test_cases": test_cases.model_dump(),
        }
    )
    if on_agent_complete:
        on_agent_complete("er_design", er)

    return FinalArtifactsPackage(
        initial_brief=initial,
        requirements=req,
        inception=inc,
        user_stories=stories,
        er_design=er,
        test_cases=test_cases,
    )