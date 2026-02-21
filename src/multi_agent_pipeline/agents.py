from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Type, cast

from pydantic import BaseModel, ValidationError

from .llm import GroqJSONClient
from .schemas import EROutput, InceptionOutput, RequirementsOutput, UserStoriesOutput


def _obj_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        return [value]
    return []


def _str_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, dict):
        result: list[str] = []
        for key, item in value.items():
            entry = f"{key}: {item}".strip()
            if entry:
                result.append(entry)
        return result
    if value is None:
        return []
    text = str(value).strip()
    return [text] if text else []


def _str_scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for key in ["description", "text", "summary", "value", "content", "title", "name"]:
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
        parts: list[str] = []
        for key, item in value.items():
            text = _str_scalar(item)
            if text:
                parts.append(f"{key}: {text}")
        return "; ".join(parts)
    if isinstance(value, list):
        parts = [_str_scalar(item) for item in value]
        parts = [part for part in parts if part]
        return "; ".join(parts)
    return str(value).strip()


def _normalize_item_ids(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in items:
        data = dict(item)
        if "id" in data and data["id"] is not None:
            data["id"] = str(data["id"])
        normalized.append(data)
    return normalized


def _normalize_requirements(raw: dict[str, Any]) -> dict[str, Any]:
    data = dict(raw) if isinstance(raw, dict) else {}
    for key in ["stakeholders", "business_goals", "constraints", "assumptions", "open_questions"]:
        data[key] = _str_list(data.get(key))
    data["functional_requirements"] = _normalize_item_ids(_obj_list(data.get("functional_requirements")))
    data["non_functional_requirements"] = _normalize_item_ids(
        _obj_list(data.get("non_functional_requirements"))
    )
    return data


def _normalize_inception(raw: dict[str, Any]) -> dict[str, Any]:
    data = dict(raw) if isinstance(raw, dict) else {}
    for key in ["product_summary", "problem_statement", "value_proposition", "release_strategy"]:
        data[key] = _str_scalar(data.get(key))
    for key in ["mvp_in_scope", "mvp_out_of_scope", "success_metrics"]:
        data[key] = _str_list(data.get(key))
    risks = _normalize_item_ids(_obj_list(data.get("risks")))
    for risk in risks:
        for key in ["description", "impact", "probability", "mitigation"]:
            risk[key] = _str_scalar(risk.get(key))
    data["risks"] = risks
    return data


# def _normalize_stories(raw: dict[str, Any]) -> dict[str, Any]:
#     data = dict(raw) if isinstance(raw, dict) else {}

#     data["epics"] = _str_list(data.get("epics"))
#     data["dependencies"] = _str_list(data.get("dependencies"))

#     stories = _normalize_item_ids(_obj_list(data.get("user_stories")))

#     for story in stories:
#         # Coerce epic to string
#         story["epic"] = _str_scalar(story.get("epic"))

#         story["acceptance_criteria"] = _str_list(
#             story.get("acceptance_criteria")
#         )

#     data["user_stories"] = stories
#     return data

def _normalize_stories(raw: dict[str, Any]) -> dict[str, Any]:
    data = dict(raw) if isinstance(raw, dict) else {}
    print(data)
    data["epics"] = _str_list(data.get("epics"))
    data["dependencies"] = _str_list(data.get("dependencies"))
    stories = _normalize_item_ids(_obj_list(data.get("user_stories")))
    for story in stories:
        story["acceptance_criteria"] = _str_list(story.get("acceptance_criteria"))
    data["user_stories"] = stories
    return data




def _normalize_er(raw: dict[str, Any]) -> dict[str, Any]:
    data = dict(raw) if isinstance(raw, dict) else {}
    data["normalization_notes"] = _str_list(data.get("normalization_notes"))
    data["design_assumptions"] = _str_list(data.get("design_assumptions"))
    entities = _obj_list(data.get("entities"))
    for entity in entities:
        entity["attributes"] = _obj_list(entity.get("attributes"))
        entity["relationships"] = _obj_list(entity.get("relationships"))
    data["entities"] = entities
    return data


def _validate_with_repair(
    llm: GroqJSONClient,
    system_prompt: str,
    payload: dict[str, Any],
    model_type: Type[BaseModel],
    normalize: Callable[[dict[str, Any]], dict[str, Any]],
) -> BaseModel:
    raw = normalize(llm.complete_json(system_prompt, payload))
    try:
        return model_type.model_validate(raw)
    except ValidationError as exc:
        repair_prompt = (
            f"{system_prompt} "
            "You must repair invalid JSON so it exactly matches the target schema. "
            "Return ONLY valid JSON."
        )
        repair_payload = {
            "original_input": payload,
            "invalid_output": raw,
            "validation_errors": exc.errors(),
        }
        repaired = normalize(llm.complete_json(repair_prompt, repair_payload))
        return model_type.model_validate(repaired)


@dataclass
class RequirementsAgent:
    llm: GroqJSONClient

    def run(self, payload: dict[str, Any]) -> RequirementsOutput:
        system_prompt = (
            "You are Agent 1 (Business Analyst). "
            "Input is JSON and output must be ONLY valid JSON. "
            "Create software requirements from the brief. "
            "Be precise but preserve uncertainty as open questions where needed."
            "Output schema keys exactly: "
            "project_name, domain, stakeholders, business_goals, functional_requirements, "
            "non_functional_requirements, constraints, assumptions, open_questions."
            "functional_requirements item keys: id,title,description,priority,rationale."
            "non_functional_requirements item keys: id,category,requirement,measurable_target."
            "priority allowed: critical|high|medium|low."
        )
        result = _validate_with_repair(
            llm=self.llm,
            system_prompt=system_prompt,
            payload=payload,
            model_type=RequirementsOutput,
            normalize=_normalize_requirements,
        )
            # print(result.model_dump_json(indent=2))
            # human_review= input("Does the output look correct? (yes/no) ")
            # if human_review.strip().lower() == "yes":
            #     break
            # print("Let's try repairing the output...")
            # if human_review.strip().lower() == "no":
            #     continue
            # print("Invalid input, please answer 'yes' or 'no'.")
        return cast(RequirementsOutput, result)


@dataclass
class InceptionAgent:
    llm: GroqJSONClient

    def run(self, payload: dict[str, Any]) -> InceptionOutput:
        system_prompt = (
            "You are Agent 2 (Product Inception). "
            "Input is JSON and output must be ONLY valid JSON. "
            "Summarize the product, define MVP scope, and identify risks. "
            "Output schema keys exactly: product_summary, problem_statement, value_proposition, "
            "mvp_in_scope, mvp_out_of_scope, risks, success_metrics, release_strategy."
            "risk item keys: id,description,impact,probability,mitigation."
            "impact/probability allowed: high|medium|low."
        )
        result = _validate_with_repair(
            llm=self.llm,
            system_prompt=system_prompt,
            payload=payload,
            model_type=InceptionOutput,
            normalize=_normalize_inception,
        )
        return cast(InceptionOutput, result)


@dataclass
class UserStoriesAgent:
    llm: GroqJSONClient

    def run(self, payload: dict[str, Any]) -> UserStoriesOutput:
        system_prompt = (
            "You are Agent 3 (Agile Analyst). "
            "Input is JSON and output must be ONLY valid JSON. "
            "Create epics and user stories with acceptance criteria. "
            "Output schema keys exactly: epics, user_stories, dependencies. "
            "user_stories item keys: id,epic,as_a,i_want,so_that,priority,acceptance_criteria. "
            "priority allowed: must|should|could. "
            "Acceptance criteria must be testable statements."
        )

        result = _validate_with_repair(
            llm=self.llm,
            system_prompt=system_prompt,
            payload=payload,
            model_type=UserStoriesOutput,
            normalize=_normalize_stories,
        )
        return cast(UserStoriesOutput, result)


@dataclass
class ERDesignAgent:
    llm: GroqJSONClient

    def run(self, payload: dict[str, Any]) -> EROutput:
        system_prompt = (
            "You are Agent 4 (Data Designer). "
            "Input is JSON and output must be ONLY valid JSON. "
            "Design a conceptual/logical ER model from product artifacts. "
            "Output schema keys exactly: entities, normalization_notes, design_assumptions. "
            "entity keys: name,description,attributes,relationships. "
            "attribute keys: name,data_type,is_primary_key,is_foreign_key,nullable,unique,description. "
            "relationship keys: to_entity,cardinality,description,foreign_key. "
            "Cardinality must use values like 1:1, 1:N, N:M."
        )
        result = _validate_with_repair(
            llm=self.llm,
            system_prompt=system_prompt,
            payload=payload,
            model_type=EROutput,
            normalize=_normalize_er,
        )
        return cast(EROutput, result)
