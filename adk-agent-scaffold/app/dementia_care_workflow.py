

from typing import Optional

from google.adk.workflow import LlmAgentNode, Workflow, node
from pydantic import BaseModel, Field


# ======================================================================================
# Step 1: Define the Pydantic Schemas for State and Node Outputs
#
# These models enforce the data structure at each step of the workflow.
# They are the contracts between your nodes.
# ======================================================================================

class InteractionAnalysis(BaseModel):
    """Structured output from the InteractionAnalyzer node."""
    agitation_level: int = Field(description="Patient's agitation level on a five-point scale.")
    summary: str = Field(description="A concise summary of the interaction.")
    rag_keyword: str = Field(description="A keyword phrase for the RAG query.")

class RagResult(BaseModel):
    """Represents the documents retrieved from the vector store."""
    retrieved_guidelines: list[str]

class DementiaCareGraphState(BaseModel):
    """
    Manages the state of the analysis pipeline as it passes through the graph.
    Each node can read from and write to this central state object.
    """
    initial_submission: str
    is_valid: bool = False
    validation_error: Optional[str] = None

    # Outputs from each step will populate the state
    interaction_analysis: Optional[InteractionAnalysis] = None
    rag_result: Optional[RagResult] = None
    # ... add fields for outputs of other steps (CareGuidance, Safety, etc.)


# ======================================================================================
# Step 2: Implement the Graph Nodes
#
# Each step in your pipeline becomes a node. We use the `@node` decorator for
# deterministic Python functions and `LlmAgentNode` for non-deterministic AI steps.
# ======================================================================================

@node
def validation_service(state: DementiaCareGraphState) -> DementiaCareGraphState:
    """
    Step 0: A deterministic code node to validate the submission.
    It checks if the input is substantial enough for analysis.
    """
    print("--- Running Step 0: Validation Service ---")
    if not state.initial_submission or len(state.initial_submission) < 20:
        state.is_valid = False
        state.validation_error = "Submission is too short or empty."
    else:
        state.is_valid = True
    return state

# Step 1: An LlmAgentNode for analyzing the interaction.
# The ADK runtime automatically calls the LLM with the prompt and injects the
# structured JSON output into the `interaction_analysis` field of the state.
interaction_analyzer_agent = LlmAgentNode(
    prompt="""
    You are the InteractionAnalyzer agent from the DementiaCare Coach system.
    Analyze the following caregiving interaction submitted by a caregiver.
    Your task is to extract key behavioral signals and summarize the event.

    Caregiver Submission:
    `{initial_submission}`

    Based on the submission, generate a response in the required JSON format.
    """,
    response_model=InteractionAnalysis,
    state_field="interaction_analysis", # The field in the state to populate
)

@node
def rag_retrieval(state: DementiaCareGraphState) -> DementiaCareGraphState:
    """
    A deterministic code node for RAG retrieval.
    This node would contain your code to query ChromaDB or Vertex AI Search.
    """
    print("--- Running RAG Retrieval ---")
    if state.interaction_analysis:
        keyword = state.interaction_analysis.rag_keyword
        print(f"Querying vector store with keyword: '{keyword}'")
        # In a real implementation, you would query your vector store here.
        # For example: `docs = chroma_client.query(keyword)`
        state.rag_result = RagResult(
            retrieved_guidelines=[f"Guideline for '{keyword}' 1", f"Guideline for '{keyword}' 2"]
        )
    return state

@node
def end_invalid(state: DementiaCareGraphState) -> DementiaCareGraphState:
    """A terminal node for handling invalid submissions gracefully."""
    print(f"--- Workflow Halted: {state.validation_error} ---")
    # Here you could also log the invalid submission or perform other cleanup.
    return state


# ======================================================================================
# Step 3: Define the Workflow Graph and Edges
#
# This is where you define the structure and control flow of your pipeline.
# Edges connect the nodes, and can be conditional.
# ======================================================================================

def should_continue_after_validation(state: DementiaCareGraphState) -> str:
    """
    This is a conditional edge. Based on the state after the `validation_service`
    node runs, it routes execution to the next appropriate node.
    """
    return "interaction_analyzer_agent" if state.is_valid else "end_invalid"

# The main workflow object that defines the graph.
dementia_care_pipeline = Workflow(
    nodes={
        "validation_service": validation_service,
        "interaction_analyzer_agent": interaction_analyzer_agent,
        "rag_retrieval": rag_retrieval,
        "end_invalid": end_invalid,
        # TODO: Add your other nodes here (ContextProcessor, SafetyEvaluator, etc.)
    },
    edges=[
        # The graph always starts at the "START" node.
        # 1. The first edge goes from START to our validation service.
        ("START", "validation_service"),

        # 2. After validation, use the conditional function to decide the next step.
        ("validation_service", should_continue_after_validation),

        # 3. The main success path continues sequentially.
        ("interaction_analyzer_agent", "rag_retrieval"),

        # 4. Define terminal states. Both paths lead to the "END" node.
        ("rag_retrieval", "END"), # TODO: Route to the next step (CareGuidance)
        ("end_invalid", "END"),
    ],
    state_model=DementiaCareGraphState,
)


# ======================================================================================
# Step 4: Example of how to invoke the workflow
#
# You would call this from your FastAPI endpoint or other application logic.
# ======================================================================================

def run_analysis_pipeline(submission_text: str):
    """
    Initializes the graph with the user's submission and runs the workflow.
    """
    print(f"\n\n>>> Running pipeline for submission: '{submission_text}'")
    initial_state = DementiaCareGraphState(initial_submission=submission_text)

    # The .run() method executes the graph from START to END.
    final_state = dementia_care_pipeline.run(initial_state)

    print("--- Workflow Finished ---")
    print("Final State:")
    print(final_state.model_dump_json(indent=2))
    return final_state

if __name__ == '__main__':
    # Example of running a valid submission
    run_analysis_pipeline(
        "My mother got very agitated when I tried to give her the morning pills. "
        "She insisted she already took them and pushed my hand away."
    )

    # Example of running an invalid submission
    run_analysis_pipeline("hello there")
