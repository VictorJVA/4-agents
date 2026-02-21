from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class InitialBriefInput(BaseModel):
    brief_text: str = Field(min_length=50)


class RequirementItem(BaseModel):
    id: str
    title: str
    description: str
    priority: Literal["critical", "high", "medium", "low"]
    rationale: str


class NonFunctionalRequirement(BaseModel):
    id: str
    category: str
    requirement: str
    measurable_target: str


class RequirementsOutput(BaseModel):
    project_name: str
    domain: str
    stakeholders: list[str]
    business_goals: list[str]
    functional_requirements: list[RequirementItem]
    non_functional_requirements: list[NonFunctionalRequirement]
    constraints: list[str]
    assumptions: list[str]
    open_questions: list[str]


class RiskItem(BaseModel):
    id: str
    description: str
    impact: Literal["high", "medium", "low"]
    probability: Literal["high", "medium", "low"]
    mitigation: str


class InceptionOutput(BaseModel):
    product_summary: str
    problem_statement: str
    value_proposition: str
    mvp_in_scope: list[str]
    mvp_out_of_scope: list[str]
    risks: list[RiskItem]
    success_metrics: list[str]
    release_strategy: str


class UserStory(BaseModel):
    id: str
    epic: str
    as_a: str
    i_want: str
    so_that: str
    priority: Literal["must", "should", "could"]
    acceptance_criteria: list[str]


class UserStoriesOutput(BaseModel):
    epics: list[str]
    user_stories: list[UserStory]
    dependencies: list[str]


class EntityAttribute(BaseModel):
    name: str
    data_type: str
    is_primary_key: bool = False
    is_foreign_key: bool = False
    nullable: bool = True
    unique: bool = False
    description: str


class Relationship(BaseModel):
    to_entity: str
    cardinality: str
    description: str
    foreign_key: str


class EntityDefinition(BaseModel):
    name: str
    description: str
    attributes: list[EntityAttribute]
    relationships: list[Relationship]


class EROutput(BaseModel):
    entities: list[EntityDefinition]
    normalization_notes: list[str]
    design_assumptions: list[str]


class TestCaseItem(BaseModel):
    id: str
    user_story_id: str
    title: str
    scenario: str
    steps: list[str]
    expected_result: str
    priority: Literal["critical", "high", "medium", "low"]
    test_type: Literal["unit", "integration", "e2e"]


class TestCasesOutput(BaseModel):
    test_cases: list[TestCaseItem]
    test_summary: str


class FinalArtifactsPackage(BaseModel):
    initial_brief: InitialBriefInput
    requirements: RequirementsOutput
    inception: InceptionOutput
    user_stories: UserStoriesOutput
    er_design: EROutput
    test_cases: TestCasesOutput
