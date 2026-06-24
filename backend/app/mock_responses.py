from app.schemas import FinalCoachingResponse, BehaviorRecognition, Recommendation, BehavioralObservation

# Mock response for Medication Refusal
MOCK_MED_REFUSAL = FinalCoachingResponse(
    observed_behavior="Medication Refusal & Theft Paranoia",
    likely_trigger="Direct correction and rushing the medication schedule",
    caregiver_pattern="Defensive, trying to logically prove the patient is wrong",
    risk_level="MEDIUM",
    recommended_response="Acknowledge the fear of theft/poisoning, remove the trigger (the pill bottle), and redirect to a calming sensory activity before offering the medication in a soft food like applesauce.",
    try_saying="I see you want to make sure your money is safe, Mom. I'll lock everything in the desk drawer. Let's have a cup of warm tea first.",
    avoid_saying="You didn't take your pills! Stop saying I'm stealing, I'm your daughter and the doctor ordered these!",
    safety_note="If cardiac medication is missed for more than 48 hours, contact her cardiologist. Ensure she does not hide pills in her mouth.",
    behavioral_timeline=[
        BehavioralObservation(
            timeframe="0:00 - 0:03",
            observable_behavior="Rapidly repeating the filler word 'iyon, iyon, iyon' ('that, that, that') while pointing dynamically to her pockets.",
            clinical_symptom="Perseveration & Word-Finding Difficulty",
            cognitive_state="Mild Frustration / Desire to Communicate: Highly motivated to explain but faces vocabulary recall barrier."
        ),
        BehavioralObservation(
            timeframe="0:04 - 0:07",
            observable_behavior="Softens voice, slows down speech, and settles on the phrases 'ganito' ('like this') when referring to her medication.",
            clinical_symptom="Circumlocution (talking around a word)",
            cognitive_state="Resignation / Searching for Validation: Adapting to inability to find the exact word by simplifying."
        ),
        BehavioralObservation(
            timeframe="0:08 - 0:13",
            observable_behavior="Delivers the line 'Ako rin namang anak ito...' ('I am also a child here...') with a steady, unblinking gaze.",
            clinical_symptom="Chronological Disorientation (Identity Shifting)",
            cognitive_state="Vulnerability / Comfort Seeking: Placing herself in the role of a child to express need for care, safety, and direction."
        )
    ],
    behavior_analysis=BehaviorRecognition(
        patient_emotion="agitated and suspicious",
        patient_triggers=["direct correction", "showing the pill bottle", "talking about doctors"],
        caregiver_communication_style="impatient, lecturing, correcting Maria's timeline",
        interaction_summary="Maria refused to take her afternoon heart medication, stating that she had already taken it and that her caregiver was trying to steal her money. The caregiver argued back, telling her she was wrong and showing her the pill bottle to 'prove' she hadn't taken it."
    ),
    strengths=[
        "Caregiver kept their voice volume relatively stable initially.",
        "Did not touch or physically force the patient."
    ],
    opportunities_for_improvement=[
        "Tried to use logic to 'prove' Maria was wrong (showing the pill bottle).",
        "Directly corrected her ('No you didn't, Mom'), which triggered defensiveness.",
        "Argued about the money accusation, causing further escalation."
    ],
    clinical_safety_flags=[
        "Potential cardiovascular medication omission risk. If missed repeatedly for >48 hours, contact cardiologist."
    ],
    coaching_scripts=[
        "Avoid saying: 'Mom, you didn't take your pills! Stop lying, I have the bottle right here.'",
        "Try saying: 'I see you're worried about these pills, Mom. They do look different today. Let's set them aside and have a cup of your favorite tea first.'",
        "Avoid saying: 'I'm not stealing your money, I'm your daughter!'",
        "Try saying: 'You want to make sure your money is safe. I'll make sure everything is locked in the drawer. Let's look at your gardening magazines.'"
    ],
    recommendations=[
        Recommendation(
            strategy_name="Validation Therapy",
            description="Acknowledge Maria's feeling of fear or mistrust instead of debating the facts. Say: 'You want to be sure you are safe, and I want that too.'",
            rationality="In moderate Alzheimer's, logical proof is rejected. Validating the emotional reality (fear of poison/theft) reduces defense mechanisms."
        ),
        Recommendation(
            strategy_name="Redirection and Pacing",
            description="Put the medication bottle away immediately. Suggest a comforting routine like making chamomile tea or playing 1950s big band music, then offer the pills again in 20-30 minutes mixed in a snack (e.g. applesauce).",
            rationality="Short-term memory lapses allow the patient to forget the previous conflict, and pairing with a preferred activity shifts their emotional valence."
        )
    ],
    detected_language="Tagalog"
)

# Mock response for Bathing Resistance
MOCK_SHOWER_RESISTANCE = FinalCoachingResponse(
    observed_behavior="Bathing Resistance & Anxiety",
    likely_trigger="Calling it a 'shower' and describing the need to get clean, highlighting memory loss",
    caregiver_pattern="Commanding, rushing, and lecturing on hygiene",
    risk_level="LOW",
    recommended_response="Reframe the task about comfort and warmth rather than hygiene. Heat the bathroom in advance, keep a dry towel draped over her shoulders for privacy, and explain steps slowly using Teepa Snow's Positive Physical Approach.",
    try_saying="Let's go get warmed up in the bathroom, Maria. I have a nice warm towel waiting for you.",
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
            observable_behavior="Mumbles 'Yesterday... yesterday...' repeatedly while looking down and touching her shirt.",
            clinical_symptom="Perseveration & Disorientation",
            cognitive_state="Defensiveness/Shame: Believes she has already showered and feels attacked by the suggestion that she is dirty."
        ),
        BehavioralObservation(
            timeframe="0:09 - 0:12",
            observable_behavior="Pushes caregiver's hand away when touched on the arm, voice raising as she speaks.",
            clinical_symptom="Tactile Defensiveness & Reactive Agitation",
            cognitive_state="Fight-or-Flight Response: The sudden physical contact triggers an automatic defensive reflex."
        )
    ],
    behavior_analysis=BehaviorRecognition(
        patient_emotion="frightened and defensive",
        patient_triggers=["calling it a 'shower'", "accusing her of smelling", "cold bathroom air"],
        caregiver_communication_style="commanding, rushed, and using physical prompts too quickly",
        interaction_summary="Maria refused to go into the bathroom for her scheduled shower, arguing that she washed yesterday. The caregiver pulled her arm slightly and raised their voice, causing Maria to push them away."
    ),
    strengths=[
        "Caregiver backed off when Maria pushed them away, avoiding physical escalation."
    ],
    opportunities_for_improvement=[
        "Accused Maria of smelling, which caused defensiveness.",
        "Attempted to pull her by the arm, creating a physical threat.",
        "Confronted her from behind instead of initiating eye contact first."
    ],
    clinical_safety_flags=[
        "Fall hazard. Patient resisting care in a wet bathroom environment has high slip risks."
    ],
    coaching_scripts=[
        "Avoid saying: 'Come on, Maria! You smell and you need to get clean!'",
        "Try saying: 'It is a bit drafty out here. Let's go get you warmed up in the bathroom. I've turned the heater on.'",
        "Avoid saying: 'No you didn't shower yesterday! Why do you keep lying?'",
        "Try saying: 'You like feeling clean and fresh. I do too. Let's go get a warm wash cloth.'"
    ],
    recommendations=[
        Recommendation(
            strategy_name="Positive Physical Approach (Teepa Snow)",
            description="Approach Maria from the front, make eye contact, offer a handshake to slide into hand-under-hand grip, and stand at her side. Walk with her rather than pulling her.",
            rationality="Approaching from the front prevents startle responses, and standing at the side is supportive rather than confrontational."
        ),
        Recommendation(
            strategy_name="Hygiene Reframing",
            description="Never use the words 'shower' or 'bath' if they trigger fear. Reframe it as 'freshening up' or 'warming up'. Use warm drapes to preserve dignity.",
            rationality="Dementia patients often develop fear of falling or sensory overload from water sprays. Preserving privacy and focusing on warmth eases the transition."
        )
    ],
    detected_language="English"
)

# Mock response for Wandering / Wants to go home
MOCK_WANDERING = FinalCoachingResponse(
    observed_behavior="Wandering & Wanting to Go Home",
    likely_trigger="Late-afternoon confusion (sundowning) combined with memory loss of her current house",
    caregiver_pattern="Reality orientation (trying to explain her parents are dead and house was sold)",
    risk_level="HIGH",
    recommended_response="Validate the desire to help her mother or go home. Ask her questions about her childhood home and farm chores to let her share memories, then redirect her to a domestic helper task like folding laundry or drinking tea.",
    try_saying="You want to make sure your mom is taken care of, Maria. She is so lucky to have you. What kind of chores did you do on the farm?",
    avoid_saying="Maria, your mom died twenty years ago! You live here with me now, your old house was sold!",
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
            cognitive_state="Sense of Duty/Regression: Living in a cognitive state of decades past, driven by the strong emotional obligation to her parents."
        ),
        BehavioralObservation(
            timeframe="0:08 - 0:12",
            observable_behavior="Screams and tries to open the door when told her mother is dead, breathing heavily.",
            clinical_symptom="Catastrophic Reaction",
            cognitive_state="Acute Grief/Panic: Hearing the reality orientation feels like receiving news of a fresh, sudden tragedy."
        )
    ],
    behavior_analysis=BehaviorRecognition(
        patient_emotion="grieving, anxious, and determined",
        patient_triggers=["sundowning shadows", "feeling trapped", "memory of farm chores"],
        caregiver_communication_style="rationalizing, corrective, stating historical facts that distress her",
        interaction_summary="Maria packed a bag at 4:30 PM, crying and stating she had to walk to her mother's farm to do the chores. The caregiver told her her mother was dead, which caused Maria to scream and try to open the front lock."
    ),
    strengths=[
        "Caregiver locked the door in advance to prevent elopement."
    ],
    opportunities_for_improvement=[
        "Used harsh reality orientation (stating her mother was dead), causing acute grief.",
        "Argued about the location, which increased her panic."
    ],
    clinical_safety_flags=[
        "High elopement and wandering risk, particularly between 4:00 PM and 7:00 PM (sundowning)."
    ],
    coaching_scripts=[
        "Avoid saying: 'Mom, your mother is dead! She died a long time ago!'",
        "Try saying: 'You really care about helping your mom. She was a wonderful cook, wasn't she? Tell me about the farm.'",
        "Avoid saying: 'You can't go out, it's dark and you don't live there anymore.'",
        "Try saying: 'The bus isn't coming for a while. Let's sit down and have some tea while we fold these towels. Your mom always liked a clean house.'"
    ],
    recommendations=[
        Recommendation(
            strategy_name="Validation & Nostalgia Therapy",
            description="Do not argue about the timeline. Validate her feelings about wanting to be helpful to her mother. Prompt her to share details of her past gardening or farm work.",
            rationality="Entering their reality preserves dignity and redirects their anxiety into pleasant reminiscence, which naturally lowers cortisol."
        ),
        Recommendation(
            strategy_name="Environmental Pacing (Sundowning)",
            description="Dim bright lights, close window blinds before sunset to block reflections and shadows, and play soft background music (1950s) to create a transition routine.",
            rationality="Shadows and reflection cause illusionary perceptions that increase confusion and the urge to flee (sundowning)."
        )
    ],
    detected_language="English"
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
    ],
    detected_language="English"
)

# ==========================================
# Mock Translation Dictionaries
# ==========================================
SPANISH_TRANSLATIONS = {
    # MOCK_MED_REFUSAL
    "Medication Refusal & Theft Paranoia": "Rechazo de medicamentos y paranoia de robo",
    "Direct correction and rushing the medication schedule": "Corrección directa y apresurar el horario de medicamentos",
    "Defensive, trying to logically prove the patient is wrong": "Defensivo, tratando de probar lógicamente que el paciente está equivocado",
    "Acknowledge the fear of theft/poisoning, remove the trigger (the pill bottle), and redirect to a calming sensory activity before offering the medication in a soft food like applesauce.": "Reconozca el temor al robo/envenenamiento, retire el desencadenante (el frasco de pastillas) y redirija a una actividad sensorial relajante antes de ofrecer el medicamento en un alimento suave como puré de manzana.",
    "I see you want to make sure your money is safe, Mom. I'll lock everything in the desk drawer. Let's have a cup of warm tea first.": "Veo que quieres asegurarte de que tu dinero esté seguro, mamá. Guardaré todo en el cajón del escritorio. Tomemos una taza de té caliente primero.",
    "You didn't take your pills! Stop saying I'm stealing, I'm your daughter and the doctor ordered these!": "¡No te tomaste tus pastillas! Deja de decir que estoy robando, ¡soy tu hija y el doctor ordenó esto!",
    "If cardiac medication is missed for more than 48 hours, contact her cardiologist. Ensure she does not hide pills in her mouth.": "Si se olvida el medicamento cardíaco por más de 48 horas, comuníquese con su cardiólogo. Asegúrese de que no esconda pastillas en la boca.",
    "Avoid saying: 'Mom, you didn't take your pills! Stop lying, I have the bottle right here.'": "Evite decir: '¡Mamá, no te tomaste tus pastillas! Deja de mentir, ¡tengo el frasco aquí mismo!'",
    "Try saying: 'I see you're worried about these pills, Mom. They do look different today. Let's set them aside and have a cup of your favorite tea first.'": "Intente decir: 'Veo que te preocupan estas pastillas, mamá. Hoy se ven diferentes. Dejémoslas a un lado y tomemos primero una taza de tu té favorito.'",
    "Avoid saying: 'I'm not stealing your money, I'm your daughter!'": "Evite decir: '¡No te estoy robando el dinero, soy tu hija!'",
    "Try saying: 'You want to make sure your money is safe. I'll make sure everything is locked in the drawer. Let's look at your gardening magazines.'": "Intente decir: 'Quieres asegurarte de que tu dinero esté seguro. Me aseguraré de que todo esté cerrado en el cajón. Miremos tus revistas de jardinería.'",
    "agitated and suspicious": "agitada y sospechosa",
    "direct correction": "corrección directa",
    "showing the pill bottle": "mostrar el frasco de pastillas",
    "talking about doctors": "hablar de médicos",
    "impatient, lecturing, correcting Maria's timeline": "impaciente, dando sermones, corrigiendo la línea de tiempo de María",
    "Maria refused to take her afternoon heart medication, stating that she had already taken it and that her caregiver was trying to steal her money. The caregiver argued back, telling her she was wrong and showing her the pill bottle to 'prove' she hadn't taken it.": "María se negó a tomar su medicamento cardíaco de la tarde, afirmando que ya lo había tomado y que su cuidadora estaba tratando de robarle el dinero. La cuidadora le discutió, diciéndole que estaba equivocada y mostrándole el frasco de pastillas para 'probar' que no lo había tomado.",
    "Caregiver kept their voice volume relatively stable initially.": "La cuidadora mantuvo el volumen de su voz relativamente estable al principio.",
    "Did not touch or physically force the patient.": "No tocó ni forzó físicamente a la paciente.",
    "Tried to use logic to 'prove' Maria was wrong (showing the pill bottle).": "Intentó usar la lógica para 'probar' que María estaba equivocada (mostrando el frasco de pastillas).",
    "Directly corrected her ('No you didn't, Mom'), which triggered defensiveness.": "La corrigió directamente ('No lo hiciste, mamá'), lo que desencadenó su actitud defensiva.",
    "Argued about the money accusation, causing further escalation.": "Discutió sobre la acusación de dinero, causando una mayor escalada.",
    "Potential cardiovascular medication omission risk. If missed repeatedly for >48 hours, contact cardiologist.": "Riesgo potencial de omisión de medicación cardiovascular. Si se omite repetidamente durante más de 48 horas, comuníquese con el cardiólogo.",

    # MOCK_SHOWER_RESISTANCE
    "Bathing Resistance & Anxiety": "Resistencia al baño y ansiedad",
    "Calling it a 'shower' and describing the need to get clean, highlighting memory loss": "Llamarlo 'ducha' y describir la necesidad de limpiarse, resaltando la pérdida de memoria",
    "Commanding, rushing, and lecturing on hygiene": "Ordenar, apresurar y dar sermones sobre la higiene",
    "Reframe the task about comfort and warmth rather than hygiene. Heat the bathroom in advance, keep a dry towel draped over her shoulders for privacy, and explain steps slowly using Teepa Snow's Positive Physical Approach.": "Reformule la tarea en torno a la comodidad y el calor en lugar de la higiene. Caliente el baño con anticipación, mantenga una toalla seca colgada sobre sus hombros para privacidad y explique los pasos lentamente usando el Enfoque Físico Positivo de Teepa Snow.",
    "Let's go get warmed up in the bathroom, Maria. I have a nice warm towel waiting for you.": "Vamos a calentarnos en el baño, María. Tengo una toalla caliente esperándote.",
    "You need to take a shower now, you smell bad and haven't washed in three days!": "¡Necesitas ducharte ahora, hueles mal y no te has lavado en tres días!",
    "Ensure grab bars are installed. High risk of slips if patient becomes physically resistant on wet tile.": "Asegúrese de instalar barras de apoyo. Alto riesgo de resbalones si la paciente se resiste físicamente sobre baldosas mojadas.",
    "frightened and defensive": "asustada y defensiva",
    "calling it a 'shower'": "llamarlo 'ducha'",
    "accusing her of smelling": "acusarla de oler mal",
    "cold bathroom air": "aire frío del baño",
    "commanding, rushed, and using physical prompts too quickly": "mandona, apresurada y usando indicaciones físicas demasiado rápido",
    "Maria refused to go into the bathroom for her scheduled shower, arguing that she washed yesterday. The caregiver pulled her arm slightly and raised their voice, causing Maria to push them away.": "María se negó a entrar al baño para su ducha programada, argumentando que se había lavado ayer. La cuidadora le tiró un poco del brazo y alzó la voz, haciendo que María la empujara.",
    "Caregiver backed off when Maria pushed them away, avoiding physical escalation.": "La cuidadora retrocedió cuando María la empujó, evitando la escalada física.",
    "Accused Maria of smelling, which caused defensiveness.": "Acusó a María de oler mal, lo que causó actitud defensiva.",
    "Attempted to pull her by the arm, creating a physical threat.": "Intentó jalarla del brazo, creando una amenaza física.",
    "Confronted her from behind instead of initiating eye contact first.": "La confrontó por detrás en lugar de iniciar contacto visual primero.",
    "Fall hazard. Patient resisting care in a wet bathroom environment has high slip risks.": "Peligro de caída. La paciente que se resiste al cuidado en un ambiente de baño húmedo tiene altos riesgos de resbalones.",
    "Avoid saying: 'Come on, Maria! You smell and you need to get clean!'": "Evite decir: '¡Vamos, María! ¡Hueles mal y necesitas limpiarte!'",
    "Try saying: 'It is a bit drafty out here. Let's go get you warmed up in the bathroom. I've turned the heater on.'": "Intente decir: 'Hace un poco de corriente aquí afuera. Vamos a calentarte en el baño. He encendido el calentador.'",
    "Avoid saying: 'No you didn't shower yesterday! Why do you keep lying?'": "Evite decir: '¡No te duchaste ayer! ¿Por qué sigues mintiendo?'",
    "Try saying: 'You like feeling clean and fresh. I do too. Let's go get a warm wash cloth.'": "Intente decir: 'Te gusta sentirte limpia y fresca. A mí también. Vamos a buscar un paño tibio.'",

    # MOCK_WANDERING
    "Wandering & Wanting to Go Home": "Deambular y querer ir a casa",
    "Late-afternoon confusion (sundowning) combined with memory loss of her current house": "Confusión a última hora de la tarde (síndrome del ocaso) combinada con la pérdida de memoria de su casa actual",
    "Reality orientation (trying to explain her parents are dead and house was sold)": "Orientación a la realidad (intentar explicarle que sus padres murieron y la casa se vendió)",
    "Validate the desire to help her mother or go home. Ask her questions about her childhood home and farm chores to let her share memories, then redirect her to a domestic helper task like folding laundry or drinking tea.": "Valide el deseo de ayudar a su madre o ir a casa. Hágale preguntas sobre su casa de la infancia y las tareas de la granja para que comparta recuerdos, luego rediríjala a una tarea doméstica como doblar la ropa o tomar té.",
    "You want to make sure your mom is taken care of, Maria. She is so lucky to have you. What kind of chores did you do on the farm?": "Quieres asegurarte de que tu mamá esté cuidada, María. Tiene mucha suerte de tenerte. ¿Qué tipo de tareas hacías en la granja?",
    "Maria, your mom died twenty years ago! You live here with me now, your old house was sold!": "¡María, tu mamá murió hace veinte años! ¡Vives aquí conmigo ahora, tu vieja casa fue vendida!",
    "Wandering risk is elevated. Install slide locks out of direct eye-line on exit doors, or use exit sensor mats.": "El riesgo de deambulación es elevado. Instale pestillos deslizantes fuera de la línea de visión directa en las puertas de salida, o use alfombrillas con sensor de salida.",
    "grieving, anxious, and determined": "en duelo, ansiosa y decidida",
    "sundowning shadows": "sombras del atardecer",
    "feeling trapped": "sentirse atrapada",
    "memory of farm chores": "recuerdo de tareas de la granja",
    "rationalizing, corrective, stating historical facts that distress her": "racionalizando, correctiva, declarando hechos históricos que la angustian",
    "Maria packed a bag at 4:30 PM, crying and stating she had to walk to her mother's farm to do the chores. The caregiver told her her mother was dead, which caused Maria to scream and try to open the front lock.": "María preparó una bolsa a las 4:30 PM, llorando y diciendo que tenía que caminar hasta la granja de su madre para hacer las tareas domésticas. La cuidadora le dijo que su madre estaba muerta, lo que hizo que María gritara e intentara abrir la cerradura delantera.",
    "Caregiver locked the door in advance to prevent elopement.": "La cuidadora cerró la puerta con llave con anticipación para evitar que se escapara.",
    "Used harsh reality orientation (stating her mother was dead), causing acute grief.": "Usó una orientación a la realidad dura (declarando que su madre estaba muerta), causando un dolor agudo.",
    "Argued about the location, which increased her panic.": "Discutió sobre la ubicación, lo que aumentó su pánico.",
    "High elopement and wandering risk, particularly between 4:00 PM and 7:00 PM (sundowning).": "Alto riesgo de fugas y deambulación, particularmente entre las 4:00 PM y las 7:00 PM (atardecer).",
    "Avoid saying: 'Mom, your mother is dead! She died a long time ago!'": "Evite decir: '¡Mamá, tu madre está muerta! ¡Murió hace mucho tiempo!'",
    "Try saying: 'You really care about helping your mom. She was a wonderful cook, wasn't she? Tell me about the farm.'": "Intente decir: 'Realmente te importa ayudar a tu mamá. Era una cocinera maravillosa, ¿verdad? Cuéntame sobre la granja.'",
    "Avoid saying: 'You can't go out, it's dark and you don't live there anymore.'": "Evite decir: 'No puedes salir, está oscuro y ya no vives allí.'",
    "Try saying: 'The bus isn't coming for a while. Let's sit down and have some tea while we fold these towels. Your mom always liked a clean house.'": "Intente decir: 'El autobús tardará un poco en llegar. Sentémonos y tomemos un té mientras doblamos estas toallas. A tu mamá siempre le gustó una casa limpia.'",

    # MOCK_DEFAULT
    "General Dementia Agitation": "Agitación general por demencia",
    "Sensory overload or unclear communication prompts": "Sobrecarga sensorial o indicaciones de comunicación poco claras",
    "Using complex, multi-step logical arguments": "Uso de argumentos lógicos complejos de múltiples pasos",
    "Acknowledge the emotional tone, simplify instructions to single-step prompts, and offer a preferred comfort preference like tea or music.": "Reconozca el tono emocional, simplifique las instrucciones a indicaciones de un solo paso y ofrezca una comodidad preferida como té o música.",
    "I hear you're feeling tired. Let's take a break and sit down. I'll make your favorite tea.": "Escucho que te sientes cansada. Tomémonos un descanso y sentémonos. Prepararé tu té favorito.",
    "You have to listen to me, we are going to do X, then Y, then Z. Why are you behaving like this?": "Tienes que escucharme, vamos a hacer X, luego Y, luego Z. ¿Por qué te comportas así?",
    "Ensure there are no physical hazards in the immediate walking path. Monitor for indicators of physical pain or discomfort.": "Asegúrese de que no haya peligros físicos en el camino inmediato. Controle los indicadores de dolor o malestar físico.",
    "confused and overwhelmed": "confundida y abrumada",
    "complex questions": "preguntas complejas",
    "loud background sounds": "sonidos de fondo fuertes",
    "using too many words and logical explanations": "usando demasiadas palabras y explicaciones lógicas",
    "The patient showed signs of confusion and minor agitation during a daily transition. The caregiver attempted to explain a complex multi-step plan.": "La paciente mostró signos de confusión y agitación menor durante una transición diaria. La cuidadora intentó explicar un plan complejo de múltiples pasos.",
    "Caregiver stopped forcing when the patient showed signs of fatigue.": "La cuidadora dejó de forzar cuando la paciente mostró signos de fatiga.",
    "Used multi-step commands instead of single, clear steps.": "Usó comandos de múltiples pasos en lugar de pasos únicos y claros.",
    "Talked too fast, which overloaded the patient's cognitive processing.": "Habló demasiado rápido, lo que sobrecargó el procesamiento cognitivo de la paciente.",
    "Monitor for cognitive fatigue. Check if patient is reporting any headache or physical discomfort.": "Monitorear la fatiga cognitiva. Compruebe si la paciente informa algún dolor de cabeza o malestar físico.",
    "Avoid saying: 'We need to put on your coat, then get the keys, then go to the car, okay?'": "Evite decir: 'Necesitamos ponernos el abrigo, luego tomar las llaves, luego ir al auto, ¿de acuerdo?'",
    "Try saying: 'Here is your coat.' (Hand it to them, wait, then follow up).": "Intente decir: 'Aquí está tu abrigo.' (Entrégaselo, espera y luego continúa).",

    # Shared terms
    "Validation Therapy": "Terapia de Validación",
    "Redirection and Pacing": "Redirección y Ritmo",
    "Positive Physical Approach (Teepa Snow)": "Enfoque Físico Positivo (Teepa Snow)",
    "Hygiene Reframing": "Reencuadre de la Higiene",
    "Validation & Nostalgia Therapy": "Terapia de Validación y Nostalgia",
    "Environmental Pacing (Sundowning)": "Ritmo Ambiental (Síndrome del Ocaso)",
    "Single-Step Command Prompting": "Indicación de Comandos de un Solo Paso"
}

TAGALOG_TRANSLATIONS = {
    # MOCK_MED_REFUSAL
    "Medication Refusal & Theft Paranoia": "Pagtanggi sa Gamot at Paranoia sa Pagnanakaw",
    "Direct correction and rushing the medication schedule": "Direktang pagwawasto at pagmamadali sa iskedyul ng gamot",
    "Defensive, trying to logically prove the patient is wrong": "Depensibo, sinusubukang patunayan sa lohikal na paraan na mali ang pasyente",
    "Acknowledge the fear of theft/poisoning, remove the trigger (the pill bottle), and redirect to a calming sensory activity before offering the medication in a soft food like applesauce.": "Tukuyin ang takot sa pagnanakaw o pagkalason, alisin ang bote ng gamot, at ibaling ang pansin sa isang nakakalma na aktibidad bago ibigay ang gamot sa malambot na pagkain tulad ng applesauce.",
    "I see you want to make sure your money is safe, Mom. I'll lock everything in the desk drawer. Let's have a cup of warm tea first.": "Nakikita ko na gusto mong siguraduhing ligtas ang pera mo, Nanay. Ila-lock ko ang lahat sa drawer ng mesa. Uminom muna tayo ng mainit na tsa.",
    "You didn't take your pills! Stop saying I'm stealing, I'm your daughter and the doctor ordered these!": "Hindi mo ininom ang mga pill mo! Ihinto mo ang pagsasabi na nagnanakaw ako, ako ang anak mo at iniutos ito ng doktor!",
    "If cardiac medication is missed for more than 48 hours, contact her cardiologist. Ensure she does not hide pills in her mouth.": "Kung lumaktaw ang gamot sa puso ng higit sa 48 oras, makipag-ugnayan sa cardiologist. Siguraduhing hindi niya itinatago ang mga tableta sa kanyang bibig.",
    "Avoid saying: 'Mom, you didn't take your pills! Stop lying, I have the bottle right here.'": "Iwasang sabihin: 'Nanay, hindi mo ininom ang mga pill mo! Huwag kang magsinungaling, narito ang bote.'",
    "Try saying: 'I see you're worried about these pills, Mom. They do look different today. Let's set them aside and have a cup of your favorite tea first.'": "Subukang sabihin: 'Nakikita kong nag-aalala ka sa mga pill na ito, Nanay. Iba nga ang hitsura nila ngayon. Itabi muna natin at uminom ng paborito mong tsa.'",
    "Avoid saying: 'I'm not stealing your money, I'm your daughter!'": "Iwasang sabihin: 'Hindi ko ninanakaw ang pera mo, ako ang anak mo!'",
    "Try saying: 'You want to make sure your money is safe. I'll make sure everything is locked in the drawer. Let's look at your gardening magazines.'": "Subukang sabihin: 'Gusto mong siguraduhing ligtas ang pera mo. Sisiguraduhin kong naka-lock ang lahat sa drawer. Tingnan natin ang mga gardening magazine mo.'",
    "agitated and suspicious": "balisa at mapaghinala",
    "direct correction": "direktang pagwawasto",
    "showing the pill bottle": "pagpapakita ng bote ng gamot",
    "talking about doctors": "pakikipag-usap tungkol sa mga doktor",
    "impatient, lecturing, correcting Maria's timeline": "walang pasensya, nanunumbat, itinutuwid ang timeline ni Maria",
    "Maria refused to take her afternoon heart medication, stating that she had already taken it and that her caregiver was trying to steal her money. The caregiver argued back, telling her she was wrong and showing her the pill bottle to 'prove' she hadn't taken it.": "Tumanggi si Maria na inumin ang kanyang gamot sa puso sa hapon, na nagsasabing nainom na niya ito at sinusubukan ng kanyang tagapag-alaga na nakawin ang kanyang pera. Sumagot ang tagapag-alaga, na sinasabing mali siya at ipinakita ang bote ng gamot upang 'patunayan' na hindi pa niya ito nainom.",
    "Caregiver kept their voice volume relatively stable initially.": "Napanatili ng tagapag-alaga na matatag ang lakas ng boses sa simula.",
    "Did not touch or physically force the patient.": "Hindi hinawakan o sapilitang ginamitan ng lakas ang pasyente.",
    "Tried to use logic to 'prove' Maria was wrong (showing the pill bottle).": "Sinubukang gumamit ng lohika upang 'patunayan' na mali si Maria (pagpapakita ng bote ng gamot).",
    "Directly corrected her ('No you didn't, Mom'), which triggered defensiveness.": "Direktang winasto siya ('Hindi, Nanay'), na nagdulot ng pagiging depensibo.",
    "Argued about the money accusation, causing further escalation.": "Nakipagtalo tungkol sa akusasyon sa pera, na nagdulot ng higit pang gulo.",
    "Potential cardiovascular medication omission risk. If missed repeatedly for >48 hours, contact cardiologist.": "Panganib sa paglaktaw ng gamot sa puso. Kung paulit-ulit na nalaktawan ng higit sa 48 oras, makipag-ugnayan sa cardiologist.",

    # MOCK_SHOWER_RESISTANCE
    "Bathing Resistance & Anxiety": "Pagtanggi sa Paliligo at Pagkabalisa",
    "Calling it a 'shower' and describing the need to get clean, highlighting memory loss": "Pagtatawag dito na 'shower' at paglalarawan sa pangangailangang maglinis, na nagpapakita ng pagkawala ng memorya",
    "Commanding, rushing, and lecturing on hygiene": "Pag-uutos, pagmamadali, at pagsesermon tungkol sa kalinisan",
    "Reframe the task about comfort and warmth rather than hygiene. Heat the bathroom in advance, keep a dry towel draped over her shoulders for privacy, and explain steps slowly using Teepa Snow's Positive Physical Approach.": "Baguhin ang pokus ng gawain sa kaginhawaan at init sa halip na kalinisan. Painitin ang banyo bago maligo, panatilihing nakabalot ang tuyong tuwalya sa kanyang balikat para sa pribadya, at ipaliwanag nang marahan ang mga hakbang gamit ang Positive Physical Approach ni Teepa Snow.",
    "Let's go get warmed up in the bathroom, Maria. I have a nice warm towel waiting for you.": "Magpainit muna tayo sa banyo, Maria. May mainit na tuwalya akong inihanda para sa iyo.",
    "You need to take a shower now, you smell bad and haven't washed in three days!": "Kailangan mo nang maligo ngayon, mabaho ka na at tatlong araw ka nang hindi naghuhugas!",
    "Ensure grab bars are installed. High risk of slips if patient becomes physically resistant on wet tile.": "Siguraduhing may nakakabit na grab bar. Mataas ang panganib na madulas kung pumalag ang pasyente sa basang sahig.",
    "frightened and defensive": "natatakot at depensibo",
    "calling it a 'shower'": "pagtawag na 'shower'",
    "accusing her of smelling": "pagbintang na mabaho siya",
    "cold bathroom air": "malamig na hangin sa banyo",
    "commanding, rushed, and using physical prompts too quickly": "nag-uutos, nagmamadali, at mabilis na gumagamit ng pisikal na paghawak",
    "Maria refused to go into the bathroom for her scheduled shower, arguing that she washed yesterday. The caregiver pulled her arm slightly and raised their voice, causing Maria to push them away.": "Tumanggi si Maria na pumunta sa banyo para sa kanyang nakatakdang shower, na nangangatwiran na naligo siya kahapon. Hinila ng tagapag-alaga ang kanyang braso nang kaunti at tinaasan ang boses, na naging sanhi upang itulak sila ni Maria.",
    "Caregiver backed off when Maria pushed them away, avoiding physical escalation.": "Umatras ang tagapag-alaga nang itulak sila ni Maria, na umiwas sa pisikal na gulo.",
    "Accused Maria of smelling, which caused defensiveness.": "Bintang na mabaho si Maria, na nagdulot ng depensa.",
    "Attempted to pull her by the arm, creating a physical threat.": "Sinubukang hilahin ang kanyang braso, na nagdulot ng takot.",
    "Confronted her from behind instead of initiating eye contact first.": "Hinarap siya mula sa likod sa halip na makipag-eye contact muna.",
    "Fall hazard. Patient resisting care in a wet bathroom environment has high slip risks.": "Panganib sa pagkadulas. Ang pasyenteng lumalaban sa basang banyo ay may mataas na panganib na madulas.",
    "Avoid saying: 'Come on, Maria! You smell and you need to get clean!'": "Iwasang sabihin: 'Dali na, Maria! Mabaho ka na at kailangan mong maglinis!'",
    "Try saying: 'It is a bit drafty out here. Let's go get you warmed up in the bathroom. I've turned the heater on.'": "Subukang sabihin: 'Medyo malamig dito sa labas. Pumunta tayo sa banyo para magpainit. Binuksan ko na ang heater.'",
    "Avoid saying: 'No you didn't shower yesterday! Why do you keep lying?'": "Iwasang sabihin: 'Hindi ka naligo kahapon! Bakit ka ba nagsisinungaling?'",
    "Try saying: 'You like feeling clean and fresh. I do too. Let's go get a warm wash cloth.'": "Subukang sabihin: 'Gusto mong maramdamang malinis at sariwa ka. Ako rin naman. Kumuha tayo ng mainit na washcloth.'",

    # MOCK_WANDERING
    "Wandering & Wanting to Go Home": "Paggala-gala at Paghahangad na Umuwi",
    "Late-afternoon confusion (sundowning) combined with memory loss of her current house": "Kalituhan sa hapon (sundowning) kasama ang pagkalimot sa kanyang kasalukuyang bahay",
    "Reality orientation (trying to explain her parents are dead and house was sold)": "Reality orientation (sinusubukang ipaliwanag na patay na ang kanyang mga magulang at naibenta na ang bahay)",
    "Validate the desire to help her mother or go home. Ask her questions about her childhood home and farm chores to let her share memories, then redirect her to a domestic helper task like folding laundry or drinking tea.": "Tukuyin ang kagustuhang tulungan ang kanyang ina o umuwi. Tanungin siya tungkol sa kanyang bahay noong bata pa at mga gawain sa bukid upang ibahagi ang kanyang mga alaala, pagkatapos ay ibaling ang pansin sa gawaing-bahay tulad ng pagtiklop ng labada o pag-inom ng tsa.",
    "You want to make sure your mom is taken care of, Maria. She is so lucky to have you. What kind of chores did you do on the farm?": "Gusto mong siguraduhing alagang-alaga ang nanay mo, Maria. Napakaswerte niya sa iyo. Anong mga gawain ang ginagawa mo sa bukid?",
    "Maria, your mom died twenty years ago! You live here with me now, your old house was sold!": "Maria, dalawampung taon nang patay ang nanay mo! Dito ka na nakatira kasama ko, naibenta na ang lumang bahay mo!",
    "Wandering risk is elevated. Install slide locks out of direct eye-line on exit doors, or use exit sensor mats.": "Mataas ang panganib sa paggala. Maglagay ng slide lock sa labas ng linya ng paningin sa mga pintuan, o gumamit ng exit sensor mat.",
    "grieving, anxious, and determined": "nagdadalamhati, balisa, at pursigido",
    "sundowning shadows": "mga anino ng sundowning",
    "feeling trapped": "pakiramdam na nakakulong",
    "memory of farm chores": "alaala ng mga gawaing-bukid",
    "rationalizing, corrective, stating historical facts that distress her": "nangangatwiran, nagtutuwid, at naglalahad ng mga detalye ng nakaraan na nagdudulot ng lungkot",
    "Maria packed a bag at 4:30 PM, crying and stating she had to walk to her mother's farm to do the chores. The caregiver told her her mother was dead, which caused Maria to scream and try to open the front lock.": "Nag-impake ng bag si Maria noong 4:30 PM, umiiyak at nagsasabing kailangan niyang maglakad papunta sa bukid ng kanyang ina para gawin ang mga gawaing-bahay. Sinabi ng tagapag-alaga na patay na ang kanyang ina, na naging dahilan upang sumigaw si Maria at subukang buksan ang lock sa harap.",
    "Caregiver locked the door in advance to prevent elopement.": "Ni-lock ng tagapag-alaga ang pinto nang maaga para maiwasan ang pag-alis.",
    "Used harsh reality orientation (stating her mother was dead), causing acute grief.": "Gumamit ng marahas na reality orientation (pagsasabi na patay na ang kanyang ina), na nagdulot ng matinding kalungkutan.",
    "Argued about the location, which increased her panic.": "Nakipagtalo tungkol sa lokasyon, na nagpalala ng kanyang takot.",
    "High elopement and wandering risk, particularly between 4:00 PM and 7:00 PM (sundowning).": "Mataas ang panganib sa paggala, lalo na sa pagitan ng 4:00 PM at 7:00 PM (sundowning).",
    "Avoid saying: 'Mom, your mother is dead! She died a long time ago!'": "Iwasang sabihin: 'Nanay, patay na ang nanay mo! Matagal na siyang namatay!'",
    "Try saying: 'You really care about helping your mom. She was a wonderful cook, wasn't she? Tell me about the farm.'": "Subukang sabihin: 'Mahalaga talaga sa iyo na tulungan ang nanay mo. Mahusay siyang magluto, hindi ba? Ikwento mo sa akin ang tungkol sa bukid.'",
    "Avoid saying: 'You can't go out, it's dark and you don't live there anymore.'": "Iwasang sabihin: 'Hindi ka pwedeng lumabas, madilim na at hindi ka na nakatira doon.'",
    "Try saying: 'The bus isn't coming for a while. Let's sit down and have some tea while we fold these towels. Your mom always liked a clean house.'": "Subukang sabihin: 'Matagal pa ang bus. Maupo muna tayo at mag-tsa habang nagtitiklop ng mga tuwalya. Gusto ng nanay mo ang malinis na bahay.'",

    # MOCK_DEFAULT
    "General Dementia Agitation": "Pangkalahatang Pagkabalisa dahil sa Demensya",
    "Sensory overload or unclear communication prompts": "Sobrang ingay/stimulus o hindi malinaw na pakikipag-usap",
    "Using complex, multi-step logical arguments": "Paggamit ng kumplikado at maraming hakbang na argumento",
    "Acknowledge the emotional tone, simplify instructions to single-step prompts, and offer a preferred comfort preference like tea or music.": "Tukuyin ang emosyon, gawing simple ang mga tagubilin sa iisang hakbang lamang, at mag-alok ng paboritong pampakalma tulad ng tsa o musika.",
    "I hear you're feeling tired. Let's take a break and sit down. I'll make your favorite tea.": "Nalalaman kong napapagod ka na. Magpahinga muna tayo at maupo. Ipaghahanda kita ng paborito mong tsa.",
    "You have to listen to me, we are going to do X, then Y, then Z. Why are you behaving like this?": "Kailangan mong makinig sa akin, gagawin natin ang X, tapos Y, tapos Z. Bakit ka ba nagkakaganyan?",
    "Ensure there are no physical hazards in the immediate walking path. Monitor for indicators of physical pain or discomfort.": "Siguraduhing walang pisikal na panganib sa lalakaran. Bantayan ang mga palatandaan ng sakit o hindi komportableng pakiramdam.",
    "confused and overwhelmed": "nalilito at nahihirapan",
    "complex questions": "kumplikadong mga tanong",
    "loud background sounds": "malalakas na tunog sa paligid",
    "using too many words and logical explanations": "paggamit ng masyadong maraming salita at lohikal na paliwanag",
    "The patient showed signs of confusion and minor agitation during a daily transition. The caregiver attempted to explain a complex multi-step plan.": "Nagpakita ang pasyente ng mga palatandaan ng kalituhan at kaunting pagkabalisa sa panahon ng pang-araw-araw na transition. Sinubukan ng tagapag-alaga na ipaliwanag ang isang kumplikadong plano.",
    "Caregiver stopped forcing when the patient showed signs of fatigue.": "Huminto ang tagapag-alaga nang magpakita ang pasyente ng pagkapagod.",
    "Used multi-step commands instead of single, clear steps.": "Gumamit ng mga utos na maraming hakbang sa halip na isa-isa lamang.",
    "Talked too fast, which overloaded the patient's cognitive processing.": "Masyadong mabilis magsalita, na nagpahirap sa pag-iisip ng pasyente.",
    "Monitor for cognitive fatigue. Check if patient is reporting any headache or physical discomfort.": "Bantayan ang pagkapagod ng isip. Suriin kung may ulat ng sakit sa ulo o pisikal na kirot ang pasyente.",
    "Avoid saying: 'We need to put on your coat, then get the keys, then go to the car, okay?'": "Iwasang sabihin: 'Kailangan nating isuot ang coat mo, tapos kukunin ang susi, tapos pupunta sa kotse, okay?'",
    "Try saying: 'Here is your coat.' (Hand it to them, wait, then follow up).": "Subukang sabihin: 'Narito ang coat mo.' (Iabot ito sa kanila, maghintay, pagkatapos ay ituloy).",

    # Shared terms
    "Validation Therapy": "Validation Therapy",
    "Redirection and Pacing": "Redirection at Pacing",
    "Positive Physical Approach (Teepa Snow)": "Positive Physical Approach (Teepa Snow)",
    "Hygiene Reframing": "Hygiene Reframing",
    "Validation & Nostalgia Therapy": "Validation at Nostalgia Therapy",
    "Environmental Pacing (Sundowning)": "Environmental Pacing (Sundowning)",
    "Single-Step Command Prompting": "Single-Step Command Prompting"
}

def get_mock_coaching_response(description: str) -> FinalCoachingResponse:
    """
    Parses key terms in the description to return the most relevant high-fidelity mock response.
    """
    d = description.lower()

    # Detect language based on simple vocabulary keywords
    detected_lang = "English"
    if any(k in d for k in ["iyon", "ganito", "anak", "salamat", "ako"]):
        detected_lang = "Tagalog"
    elif any(k in d for k in ["hola", "pastillas", "madre", "casa", "baño", "gracias"]):
        detected_lang = "Spanish"

    if any(k in d for k in ["med", "pill", "tablet", "doctor", "poison", "steal", "20260623_205611", "sample_vid"]):
        response = MOCK_MED_REFUSAL.model_copy(deep=True)
        response.detected_language = "Tagalog" if ("20260623_205611" in d or "sample_vid" in d or detected_lang == "Tagalog") else detected_lang
        return response
    elif any(k in d for k in ["shower", "bath", "wash", "dirty", "clean", "bathroom"]):
        response = MOCK_SHOWER_RESISTANCE.model_copy(deep=True)
        response.detected_language = detected_lang
        return response
    elif any(k in d for k in ["home", "mother", "suitcase", "farm", "bus", "leave"]):
        response = MOCK_WANDERING.model_copy(deep=True)
        response.detected_language = detected_lang
        return response

    response = MOCK_DEFAULT.model_copy(deep=True)
    response.detected_language = detected_lang
    return response

def get_mock_translation(response: FinalCoachingResponse, target_language: str) -> FinalCoachingResponse:
    if target_language == response.detected_language:
        return response

    t_map = {}
    lang_code = ""
    if target_language == "Spanish":
        t_map = SPANISH_TRANSLATIONS
        lang_code = "[ES]"
    elif target_language == "Tagalog":
        t_map = TAGALOG_TRANSLATIONS
        lang_code = "[TL]"
    else:
        # Default fallback to original
        return response

    def t(text: str) -> str:
        if not text:
            return text
        cleaned = text.strip()
        if cleaned in t_map:
            return t_map[cleaned]
        # Check if it has a prefix
        for en, foreign in t_map.items():
            if en in text:
                return text.replace(en, foreign)
        return f"{lang_code} {text}"

    translated = response.model_copy(deep=True)
    translated.observed_behavior = t(translated.observed_behavior)
    translated.likely_trigger = t(translated.likely_trigger)
    translated.caregiver_pattern = t(translated.caregiver_pattern)
    translated.recommended_response = t(translated.recommended_response)
    translated.try_saying = t(translated.try_saying)
    translated.avoid_saying = t(translated.avoid_saying)
    translated.safety_note = t(translated.safety_note)

    translated.strengths = [t(s) for s in translated.strengths]
    translated.opportunities_for_improvement = [t(o) for o in translated.opportunities_for_improvement]
    translated.clinical_safety_flags = [t(c) for c in translated.clinical_safety_flags]
    translated.coaching_scripts = [t(cs) for cs in translated.coaching_scripts]

    translated.behavior_analysis.patient_emotion = t(translated.behavior_analysis.patient_emotion)
    translated.behavior_analysis.caregiver_communication_style = t(translated.behavior_analysis.caregiver_communication_style)
    translated.behavior_analysis.interaction_summary = t(translated.behavior_analysis.interaction_summary)
    translated.behavior_analysis.patient_triggers = [t(pt) for pt in translated.behavior_analysis.patient_triggers]

    for obs in translated.behavioral_timeline:
        obs.observable_behavior = t(obs.observable_behavior)
        obs.clinical_symptom = t(obs.clinical_symptom)
        obs.cognitive_state = t(obs.cognitive_state)

    for rec in translated.recommendations:
        rec.strategy_name = t(rec.strategy_name)
        rec.description = t(rec.description)
        rec.rationality = t(rec.rationality)

    return translated
