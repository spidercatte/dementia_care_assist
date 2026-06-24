from app.schemas import FinalCoachingResponse, BehaviorRecognition, Recommendation, BehavioralObservation

# Mock response for Medication Refusal
MOCK_MED_REFUSAL = FinalCoachingResponse(
    observed_behavior="Medication Refusal & Theft Paranoia",
    likely_trigger="Direct correction and rushing the medication schedule",
    caregiver_pattern="Defensive, trying to logically prove the patient is wrong",
    risk_level="MEDIUM",
    recommended_response="Acknowledge the fear of theft/poisoning, remove the trigger (the pill bottle), and redirect to a calming sensory activity before offering the medication in a soft food like applesauce.",
    try_saying="I see you want to make sure your money is safe, Dad. I'll lock everything in the desk drawer. Let's have a cup of warm tea first.",
    avoid_saying="You didn't take your pills! Stop saying I'm stealing, I'm your daughter and the doctor ordered these!",
    safety_note="If cardiac medication is missed for more than 48 hours, contact his cardiologist. Ensure he does not hide pills in his mouth.",
    behavioral_timeline=[
        BehavioralObservation(
            timeframe="0:00 - 0:03",
            observable_behavior="Rapidly repeating the filler word 'iyon, iyon, iyon' ('that, that, that') while pointing dynamically to his pockets.",
            clinical_symptom="Perseveration & Word-Finding Difficulty",
            cognitive_state="Mild Frustration / Desire to Communicate: Highly motivated to explain but faces vocabulary recall barrier."
        ),
        BehavioralObservation(
            timeframe="0:04 - 0:07",
            observable_behavior="Softens voice, slows down speech, and settles on the phrases 'ganito' ('like this') when referring to his medication.",
            clinical_symptom="Circumlocution (talking around a word)",
            cognitive_state="Resignation / Searching for Validation: Adapting to inability to find the exact word by simplifying."
        ),
        BehavioralObservation(
            timeframe="0:08 - 0:13",
            observable_behavior="Delivers the line 'Ako rin namang anak ito...' ('I am also a child here...') with a steady, unblinking gaze.",
            clinical_symptom="Chronological Disorientation (Identity Shifting)",
            cognitive_state="Vulnerability / Comfort Seeking: Placing himself in the role of a child to express need for care, safety, and direction."
        )
    ],
    behavior_analysis=BehaviorRecognition(
        patient_emotion="agitated and suspicious",
        patient_triggers=["direct correction", "showing the pill bottle", "talking about doctors"],
        caregiver_communication_style="impatient, lecturing, correcting Arthur's timeline",
        interaction_summary="Arthur refused to take his afternoon heart medication, stating that he had already taken it and that his caregiver was trying to steal his money. The caregiver argued back, telling him he was wrong and showing him the pill bottle to 'prove' he hadn't taken it."
    ),
    strengths=[
        "Caregiver kept their voice volume relatively stable initially.",
        "Did not touch or physically force the patient."
    ],
    opportunities_for_improvement=[
        "Tried to use logic to 'prove' Arthur was wrong (showing the pill bottle).",
        "Directly corrected him ('No you didn't, Dad'), which triggered defensiveness.",
        "Argued about the money accusation, causing further escalation."
    ],
    clinical_safety_flags=[
        "Potential cardiovascular medication omission risk. If missed repeatedly for >48 hours, contact cardiologist."
    ],
    coaching_scripts=[
        "Avoid saying: 'Dad, you didn't take your pills! Stop lying, I have the bottle right here.'",
        "Try saying: 'I see you're worried about these pills, Dad. They do look different today. Let's set them aside and have a cup of your favorite tea first.'",
        "Avoid saying: 'I'm not stealing your money, I'm your daughter!'",
        "Try saying: 'You want to make sure your money is safe. I'll make sure everything is locked in the drawer. Let's look at your carpentry magazines.'"
    ],
    recommendations=[
        Recommendation(
            strategy_name="Validation Therapy",
            description="Acknowledge Arthur's feeling of fear or mistrust instead of debating the facts. Say: 'You want to be sure you are safe, and I want that too.'",
            rationality="In moderate Alzheimer's, logical proof is rejected. Validating the emotional reality (fear of poison/theft) reduces defense mechanisms."
        ),
        Recommendation(
            strategy_name="Redirection and Pacing",
            description="Put the medication bottle away immediately. Suggest a comforting routine like making chamomile tea or playing 1950s big band music, then offer the pills again in 20-30 minutes mixed in a snack (e.g. applesauce).",
            rationality="Short-term memory lapses allow the patient to forget the previous conflict, and pairing with a preferred activity shifts their emotional valence."
        )
    ]
)

# Mock response for Bathing Resistance
MOCK_SHOWER_RESISTANCE = FinalCoachingResponse(
    observed_behavior="Bathing Resistance & Anxiety",
    likely_trigger="Calling it a 'shower' and describing the need to get clean, highlighting memory loss",
    caregiver_pattern="Commanding, rushing, and lecturing on hygiene",
    risk_level="LOW",
    recommended_response="Reframe the task about comfort and warmth rather than hygiene. Heat the bathroom in advance, keep a dry towel draped over his shoulders for privacy, and explain steps slowly using Teepa Snow's Positive Physical Approach.",
    try_saying="Let's go get warmed up in the bathroom, Arthur. I have a nice warm towel waiting for you.",
    avoid_saying="You need to take a shower now, you smell bad and haven't washed in three days!",
    safety_note="Ensure grab bars are installed. High risk of slips if patient becomes physically resistant on wet tile.",
    behavioral_timeline=[
        BehavioralObservation(
            timeframe="0:00 - 0:04",
            observable_behavior="Steps backward away from the bathroom door, shaking head side to side and crossing arms.",
            clinical_symptom="Oppositional Behavior & Gestural Avoidance",
            cognitive_state="Fear/Defense: Feeling threatened by the request or the prospect of sensory discomfort."
        ),
        BehavioralObservation(
            timeframe="0:05 - 0:08",
            observable_behavior="Mumbles 'Yesterday... yesterday...' repeatedly while looking down and touching his shirt.",
            clinical_symptom="Perseveration & Disorientation",
            cognitive_state="Defensiveness/Shame: Believes he has already showered and feels attacked by the suggestion that he is dirty."
        ),
        BehavioralObservation(
            timeframe="0:09 - 0:12",
            observable_behavior="Pushes caregiver's hand away when touched on the arm, voice raising as he speaks.",
            clinical_symptom="Tactile Defensiveness & Reactive Agitation",
            cognitive_state="Fight-or-Flight Response: The sudden physical contact triggers an automatic defensive reflex."
        )
    ],
    behavior_analysis=BehaviorRecognition(
        patient_emotion="frightened and defensive",
        patient_triggers=["calling it a 'shower'", "accusing him of smelling", "cold bathroom air"],
        caregiver_communication_style="demanding, rushed, and using physical prompts too quickly",
        interaction_summary="Arthur refused to go into the bathroom for his scheduled shower, arguing that he washed yesterday. The caregiver pulled his arm slightly and raised their voice, causing Arthur to push them away."
    ),
    strengths=[
        "Caregiver backed off when Arthur pushed them away, avoiding physical escalation."
    ],
    opportunities_for_improvement=[
        "Accused Arthur of smelling, which caused defensiveness.",
        "Attempted to pull him by the arm, creating a physical threat.",
        "Confronted him from behind instead of initiating eye contact first."
    ],
    clinical_safety_flags=[
        "Fall hazard. Patient resisting care in a wet bathroom environment has high slip risks."
    ],
    coaching_scripts=[
        "Avoid saying: 'Come on, Arthur! You smell and you need to get clean!'",
        "Try saying: 'It is a bit drafty out here. Let's go get you warmed up in the bathroom. I've turned the heater on.'",
        "Avoid saying: 'No you didn't shower yesterday! Why do you keep lying?'",
        "Try saying: 'You like feeling clean and fresh. I do too. Let's go get a warm wash cloth.'"
    ],
    recommendations=[
        Recommendation(
            strategy_name="Positive Physical Approach (Teepa Snow)",
            description="Approach Arthur from the front, make eye contact, offer a handshake to slide into hand-under-hand grip, and stand at his side. Walk with him rather than pulling him.",
            rationality="Approaching from the front prevents startle responses, and standing at the side is supportive rather than confrontational."
        ),
        Recommendation(
            strategy_name="Hygiene Reframing",
            description="Never use the words 'shower' or 'bath' if they trigger fear. Reframe it as 'freshening up' or 'warming up'. Use warm drapes to preserve dignity.",
            rationality="Dementia patients often develop fear of falling or sensory overload from water sprays. Preserving privacy and focusing on warmth eases the transition."
        )
    ]
)

# Mock response for Wandering / Wants to go home
MOCK_WANDERING = FinalCoachingResponse(
    observed_behavior="Wandering & Wanting to Go Home",
    likely_trigger="Late-afternoon confusion (sundowning) combined with memory loss of his current house",
    caregiver_pattern="Reality orientation (trying to explain his parents are dead and house was sold)",
    risk_level="HIGH",
    recommended_response="Validate the desire to help his mother or go home. Ask him questions about his childhood home and farm chores to let him share memories, then redirect him to a domestic helper task like folding laundry or drinking tea.",
    try_saying="You want to make sure your mom is taken care of, Arthur. She is so lucky to have you. What kind of chores did you do on the farm?",
    avoid_saying="Arthur, your mom died twenty years ago! You live here with me now, your old house was sold!",
    safety_note="Wandering risk is elevated. Install slide locks out of direct eye-line on exit doors, or use exit sensor mats.",
    behavioral_timeline=[
        BehavioralObservation(
            timeframe="0:00 - 0:03",
            observable_behavior="Paces back and forth near the front door, repeatedly checking the lock and window.",
            clinical_symptom="Psychomotor Agitation & Exit Seeking",
            cognitive_state="Anxiety/Displacement: Driven by an internal urgency to go somewhere else to feel secure."
        ),
        BehavioralObservation(
            timeframe="0:04 - 0:07",
            observable_behavior="Pulls a suitcase, tearfully repeating 'My mother is waiting... she needs help on the farm.'",
            clinical_symptom="Chronological Disorientation & Past Role Reliving",
            cognitive_state="Sense of Duty/Regression: Living in a cognitive state of decades past, driven by the strong emotional obligation to his parents."
        ),
        BehavioralObservation(
            timeframe="0:08 - 0:12",
            observable_behavior="Screams and tries to open the door when told his mother is dead, breathing heavily.",
            clinical_symptom="Catastrophic Reaction",
            cognitive_state="Acute Grief/Panic: Hearing the reality orientation feels like receiving news of a fresh, sudden tragedy."
        )
    ],
    behavior_analysis=BehaviorRecognition(
        patient_emotion="grieving, anxious, and determined",
        patient_triggers=["sundowning shadows", "feeling trapped", "memory of farm chores"],
        caregiver_communication_style="rationalizing, corrective, stating historical facts that distress him",
        interaction_summary="Arthur packed a bag at 4:30 PM, crying and stating he had to walk to his mother's farm to do the chores. The caregiver told him his mother was dead, which caused Arthur to scream and try to open the front lock."
    ),
    strengths=[
        "Caregiver locked the door in advance to prevent elopement."
    ],
    opportunities_for_improvement=[
        "Used harsh reality orientation (stating his mother was dead), causing acute grief.",
        "Argued about the location, which increased his panic."
    ],
    clinical_safety_flags=[
        "High elopement and wandering risk, particularly between 4:00 PM and 7:00 PM (sundowning)."
    ],
    coaching_scripts=[
        "Avoid saying: 'Dad, your mother is dead! She died a long time ago!'",
        "Try saying: 'You really care about helping your mom. She was a wonderful cook, wasn't she? Tell me about the farm.'",
        "Avoid saying: 'You can't go out, it's dark and you don't live there anymore.'",
        "Try saying: 'The bus isn't coming for a while. Let's sit down and have some tea while we fold these towels. Your mom always liked a clean house.'"
    ],
    recommendations=[
        Recommendation(
            strategy_name="Validation & Nostalgia Therapy",
            description="Do not argue about the timeline. Validate his feelings about wanting to be helpful to his mother. Prompt him to share details of his past carpentry or farm work.",
            rationality="Entering their reality preserves dignity and redirects their anxiety into pleasant reminiscence, which naturally lowers cortisol."
        ),
        Recommendation(
            strategy_name="Environmental Pacing (Sundowning)",
            description="Dim bright lights, close window blinds before sunset to block reflections and shadows, and play soft background music (1950s) to create a transition routine.",
            rationality="Shadows and reflection cause illusionary perceptions that increase confusion and the urge to flee (sundowning)."
        )
    ]
)

# Default / Fallback Response
MOCK_DEFAULT = FinalCoachingResponse(
    observed_behavior="General Dementia Agitation",
    likely_trigger="Sensory overload or unclear communication prompts",
    caregiver_pattern="Using complex, multi-step logical arguments",
    risk_level="LOW",
    recommended_response="Acknowledge the emotional tone, simplify instructions to single-step prompts, and offer a preferred comfort preference like tea or music.",
    try_saying="I hear you're feeling tired. Let's take a break and sit down. I'll make your favorite tea.",
    avoid_saying="You have to listen to me, we are going to do X, then Y, then Z. Why are you behaving like this?",
    safety_note="Ensure there are no physical hazards in the immediate walking path. Monitor for indicators of physical pain or discomfort.",
    behavioral_timeline=[
        BehavioralObservation(
            timeframe="0:00 - 0:04",
            observable_behavior="Stares blankly at the caregiver for several seconds after a multi-step instruction is given.",
            clinical_symptom="Delayed Processing & Receptive Aphasia",
            cognitive_state="Cognitive Overload: Striving to make sense of verbal inputs that exceed processing capacity."
        ),
        BehavioralObservation(
            timeframe="0:05 - 0:08",
            observable_behavior="Fidgets with coat buttons, sighing and turning away from the caregiver.",
            clinical_symptom="Purposeless Motor Activity & Avoidance",
            cognitive_state="Frustration/Fatigue: Frustrated by the inability to complete the task, leading to withdrawal."
        )
    ],
    behavior_analysis=BehaviorRecognition(
        patient_emotion="confused and overwhelmed",
        patient_triggers=["complex questions", "loud background sounds"],
        caregiver_communication_style="using too many words and logical explanations",
        interaction_summary="The patient showed signs of confusion and minor agitation during a daily transition. The caregiver attempted to explain a complex multi-step plan."
    ),
    strengths=[
        "Caregiver stopped forcing when the patient showed signs of fatigue."
    ],
    opportunities_for_improvement=[
        "Used multi-step commands instead of single, clear steps.",
        "Talked too fast, which overloaded the patient's cognitive processing."
    ],
    clinical_safety_flags=[
        "Monitor for cognitive fatigue. Check if patient is reporting any headache or physical discomfort."
    ],
    coaching_scripts=[
        "Avoid saying: 'We need to put on your coat, then get the keys, then go to the car, okay?'",
        "Try saying: 'Here is your coat.' (Hand it to them, wait, then follow up)."
    ],
    recommendations=[
        Recommendation(
            strategy_name="Single-Step Command Prompting",
            description="Break down all instructions into single, action-oriented prompts. Hand objects to them one by one rather than instructing them verbally.",
            rationality="Dementia damages executive function and sequence processing. Single-step prompts eliminate the frustration of forgetting instructions midway."
        )
    ]
)

def get_mock_coaching_response(description: str) -> FinalCoachingResponse:
    """
    Parses key terms in the description to return the most relevant high-fidelity mock response.
    """
    d = description.lower()
    if any(k in d for k in ["med", "pill", "tablet", "doctor", "poison", "steal", "20260623_205611", "sample_vid"]):
        return MOCK_MED_REFUSAL
    elif any(k in d for k in ["shower", "bath", "wash", "dirty", "clean", "bathroom"]):
        return MOCK_SHOWER_RESISTANCE
    elif any(k in d for k in ["home", "mother", "suitcase", "farm", "bus", "leave"]):
        return MOCK_WANDERING
    return MOCK_DEFAULT
