from typing import List, Optional
from pydantic import BaseModel, Field

# ==========================================
# 1. Interaction Analysis Agent Schema
# ==========================================
class InteractionAnalysisResponse(BaseModel):
    observed_behavior: str = Field(description="Summary of the behavior observed (e.g. medication refusal, physical resistance)")
    likely_trigger: str = Field(description="Identified trigger (verbal, environmental, tone) that initiated the behavior")
    caregiver_pattern: str = Field(description="Assessment of caregiver response style (e.g. direct correction, arguing, validation)")
    agitation_level: int = Field(description="Agitation level on scale of 1 (calm) to 10 (extremely combative)")
    confusion_level: int = Field(description="Confusion/disorientation level on scale of 1 (lucid) to 10 (severe)")
    verbal_transcript_summary: str = Field(description="Summary of verbal exchange")
    non_verbal_cues: str = Field(description="Observed non-verbal cues (pacing, tone, posture, expressions)")
    rag_query: str = Field(description="2-3 keywords to search for care guidelines (e.g., 'medication refusal', 'shower resistance')")

# ==========================================
# 2. Patient Context Agent Schema
# ==========================================
class PatientContextResponse(BaseModel):
    clinical_stage: str = Field(description="Dementia type and staging")
    active_triggers: List[str] = Field(description="Known triggers from the history that are relevant now")
    preferences: List[str] = Field(description="Comfort habits, likes, or tools they respond well to")
    daily_routine_constraints: List[str] = Field(description="Routines, timings, or schedules to keep in mind")
    health_risk_factors: List[str] = Field(description="Relevant health concerns (diabetes, pain, sleep patterns)")

# ==========================================
# 3. Care Guidance Agent Schema
# ==========================================
class CareGuidanceResponse(BaseModel):
    retrieved_guidelines: List[str] = Field(description="Title/IDs of retrieved guidelines")
    recommended_response: str = Field(description="Clinical advice from nursing, occupational therapy, or validation protocols")
    do_nots: List[str] = Field(description="Specific things the caregiver must NOT do in this situation")

# ==========================================
# 4. Safety & Escalation Agent Schema
# ==========================================
class SafetyEscalationResponse(BaseModel):
    risk_level: str = Field(description="Safety risk: LOW, MEDIUM, HIGH, EMERGENCY")
    safety_note: str = Field(description="Critical safety instruction (e.g. check for pain, fall hazards, delirium/UTI)")
    escalate_to_clinician: bool = Field(description="True if a physician, occupational therapist, or emergency services should be contacted")

# ==========================================
# 5. Caregiver Coaching Agent Schema (Final Combined Output)
# ==========================================
class BehaviorRecognition(BaseModel):
    patient_emotion: str = Field(description="Primary emotional state of the patient")
    patient_triggers: List[str] = Field(description="Identified triggers that escalated the distress")
    caregiver_communication_style: str = Field(description="Assessment of the caregiver's style")
    interaction_summary: str = Field(description="Summary of what happened")

class Recommendation(BaseModel):
    strategy_name: str = Field(description="Name of the therapy or method suggested")
    description: str = Field(description="Actionable explanation of how to apply it")
    rationality: str = Field(description="The scientific/clinical rationale behind it")

class FinalCoachingResponse(BaseModel):
    observed_behavior: str = Field(description="Observed behavioral symptom")
    likely_trigger: str = Field(description="Likely trigger of distress")
    caregiver_pattern: str = Field(description="Caregiver communication pattern identified")
    risk_level: str = Field(description="Safety risk level (e.g., LOW, MEDIUM, HIGH)")
    recommended_response: str = Field(description="Synthesized caregiver intervention recommendation")
    try_saying: str = Field(description="Empathetic script or phrase the caregiver should use")
    avoid_saying: str = Field(description="Specific logical/corrective phrase the caregiver should avoid")
    safety_note: str = Field(description="Immediate safety warnings or clinical instructions")

    # Matching UI Expectations
    behavior_analysis: BehaviorRecognition = Field(description="Combined behavior details")
    strengths: List[str] = Field(description="What the caregiver did well")
    opportunities_for_improvement: List[str] = Field(description="Things the caregiver should change")
    clinical_safety_flags: List[str] = Field(description="List of clinical safety warnings")
    coaching_scripts: List[str] = Field(description="Dialogue pairs ('Avoid: ...', 'Try: ...')")
    recommendations: List[Recommendation] = Field(description="List of detailed recommendation cards")
