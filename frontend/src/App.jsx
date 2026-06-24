import React, { useState, useEffect, useRef } from 'react';
import {
  Activity,
  User,
  Gamepad2,
  BookOpen,
  Upload,
  MessageSquare,
  AlertTriangle,
  Heart,
  Smile,
  ThumbsUp,
  CheckCircle2,
  Trash2,
  Plus,
  Search,
  Database,
  Sparkles,
  RefreshCw,
  Info,
  Clock,
  Video,
  VideoOff,
  Mic,
  Square,
  Volume2,
  Circle,
  Sun,
  Moon
} from 'lucide-react';

const BACKEND_URL = 'http://localhost:8000';

// Mock data fallbacks for demonstration when backend is offline
const MOCK_PATIENT = {
  name: "Maria",
  dementia_type: "Alzheimer's (Moderate Stage)",
  triggers: ["direct correction", "being rushed", "loud noises", "asking 'do you remember?'"],
  preferences: ["listening to 1950s big band music", "drinking chamomile tea", "talking about her past work as a gardener"],
  background: "Maria is 78 years old. She lives at home with her daughter who is her primary caregiver. She often gets confused in the late afternoon (sundowning) and can refuse medication or personal care because she believes she has to go to work or that her daughter is trying to poison her."
};

const MOCK_ANALYSIS_MED_REFUSAL = {
  behavior_analysis: {
    patient_emotion: "agitated and suspicious",
    patient_triggers: ["direct correction ('you must take this now')", "rushing"],
    caregiver_communication_style: "impatient, lecturing, correcting Maria's timeline",
    interaction_summary: "Maria refused to take her afternoon heart medication, stating that she had already taken it and that her caregiver was trying to steal her money. The caregiver argued back, telling her she was wrong and showing her the pill bottle to 'prove' she hadn't taken it, which escalated Maria's shouting."
  },
  behavioral_timeline: [
    {
      timeframe: "0:00 - 0:03",
      observable_behavior: "Rapidly repeating the filler word 'iyon, iyon, iyon' ('that, that, that') while pointing dynamically to her pockets.",
      clinical_symptom: "Perseveration & Word-Finding Difficulty",
      cognitive_state: "Mild Frustration / Desire to Communicate: Highly motivated to explain but faces vocabulary recall barrier."
    },
    {
      timeframe: "0:04 - 0:07",
      observable_behavior: "Softens voice, slows down speech, and settles on the phrases 'ganito' ('like this') when referring to her medication.",
      clinical_symptom: "Circumlocution (talking around a word)",
      cognitive_state: "Resignation / Searching for Validation: Adapting to inability to find the exact word by simplifying."
    },
    {
      timeframe: "0:08 - 0:13",
      observable_behavior: "Delivers the line 'Ako rin namang anak ito...' ('I am also a child here...') with a steady, unblinking gaze.",
      clinical_symptom: "Chronological Disorientation (Identity Shifting)",
      cognitive_state: "Vulnerability / Comfort Seeking: Placing herself in the role of a child to express need for care, safety, and direction."
    }
  ],
  strengths: [
    "Caregiver kept their voice volume relatively stable initially.",
    "Did not touch or physically force the patient."
  ],
  opportunities_for_improvement: [
    "Tried to use logic to 'prove' Maria was wrong (showing the pill bottle).",
    "Directly corrected her ('No you didn't, Mom'), which triggered defensiveness.",
    "Argued about the money accusation, causing further escalation."
  ],
  clinical_safety_flags: [
    "Potential cardiovascular medication omission risk. If missed repeatedly for >48 hours, contact cardiologist."
  ],
  coaching_scripts: [
    "Avoid saying: 'Mom, you didn't take your pills! Stop lying, I have the bottle right here.'",
    "Try saying: 'I see you're worried about these pills, Mom. They do look different today. Let's set them aside and have a cup of your favorite tea first.'",
    "Avoid saying: 'I'm not stealing your money, I'm your daughter!'",
    "Try saying: 'You want to make sure your money is safe. I'll make sure everything is locked in the drawer. Let's look at your gardening magazines.'"
  ],
  recommendations: [
    {
      strategy_name: "Validation Therapy",
      description: "Acknowledge Maria's feeling of fear or mistrust instead of debating the facts. Say: 'You want to be sure you are safe, and I want that too.'",
      rationality: "In moderate Alzheimer's, logical proof is rejected. Validating the emotional reality (fear of poison/theft) reduces defense mechanisms."
    },
    {
      strategy_name: "Redirection and Pacing",
      description: "Put the medication bottle away immediately. Suggest a comforting routine like making chamomile tea or playing 1950s big band music, then offer the pills again in 20-30 minutes mixed in a snack (e.g. applesauce).",
      rationality: "Short-term memory lapses allow the patient to forget the previous conflict, and pairing with a preferred activity shifts their emotional valence."
    }
  ]
};

const MOCK_SCENARIOS = [
  {
    id: "med_refusal",
    title: "Medication Refusal",
    description: "Maria refuses her heart medication, insisting she already took it and accusing you of trying to poison her.",
    initial_dialogue: "I'm not taking those pills! You already gave them to me this morning. You're trying to make me sick so you can take my house!",
    initial_agitation: 6
  },
  {
    id: "shower_refusal",
    title: "Shower Agitation",
    description: "It is late afternoon and Maria resists taking a shower. She gets defensive and says she just showered yesterday.",
    initial_dialogue: "Why are you always nagging me to wash? I took a shower yesterday! Leave me alone, I'm clean enough!",
    initial_agitation: 5
  },
  {
    id: "go_home",
    title: "Wants to 'Go Home'",
    description: "Maria starts packing a small bag in the living room. She is crying and saying she needs to go to her mother's house.",
    initial_dialogue: "Where is my suitcase? I have to go home right now. My mother is waiting for me to help with the farm chores. Let me out!",
    initial_agitation: 7
  }
];

function App() {
  // Theme State
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };



  // Navigation & Config State
  const [activeTab, setActiveTab] = useState('dashboard');
  const [backendStatus, setBackendStatus] = useState('checking'); // checking, online, offline
  const [isSeeding, setIsSeeding] = useState(false);

  // Patient Profile State
  const [patient, setPatient] = useState(MOCK_PATIENT);
  const [newTrigger, setNewTrigger] = useState('');
  const [newPreference, setNewPreference] = useState('');
  const [isSavingProfile, setIsSavingProfile] = useState(false);

  // Analysis State
  const [inputText, setInputText] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisStep, setAnalysisStep] = useState(0); // 0: Idle, 1: Interaction Analysis, 2: Context Evaluation, 3: Guideline RAG, 4: Safety Assessment, 5: Coaching Synthesis

  // Live Recording & Preview State
  const [fileUrl, setFileUrl] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [recordingType, setRecordingType] = useState('video'); // 'video' or 'audio'
  const [showRecorder, setShowRecorder] = useState(false);

  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const videoPreviewRef = useRef(null);
  const recordingIntervalRef = useRef(null);
  const chunksRef = useRef([]);

  // Clean up recording stream & timer
  const cleanupRecording = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (recordingIntervalRef.current) {
      clearInterval(recordingIntervalRef.current);
      recordingIntervalRef.current = null;
    }
    setIsRecording(false);
    setRecordingTime(0);
  };

  useEffect(() => {
    return () => cleanupRecording();
  }, []);

  const startRecording = async (type = 'video') => {
    cleanupRecording();
    setRecordingType(type);
    chunksRef.current = [];

    try {
      const constraints = {
        audio: true,
        video: type === 'video' ? { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" } : false
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;

      if (type === 'video' && videoPreviewRef.current) {
        videoPreviewRef.current.srcObject = stream;
      }

      let mimeType = type === 'video' ? 'video/webm;codecs=vp9,opus' : 'audio/webm;codecs=opus';
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = type === 'video' ? 'video/webm' : 'audio/webm';
      }

      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mediaRecorder.mimeType });
        const ext = mediaRecorder.mimeType.includes('video') ? 'webm' : 'weba';
        const filename = `live-recording-${Date.now()}.${ext}`;
        const file = new File([blob], filename, { type: mediaRecorder.mimeType });

        setSelectedFile(file);
        setInputText('');

        if (fileUrl) URL.revokeObjectURL(fileUrl);
        setFileUrl(URL.createObjectURL(file));

        cleanupRecording();
        setShowRecorder(false);
      };

      mediaRecorder.start(100); // chunk every 100ms
      setIsRecording(true);

      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(t => t + 1);
      }, 1000);

    } catch (err) {
      console.error("Error starting recording:", err);
      alert("Could not access camera or microphone. Please check permissions.");
      cleanupRecording();
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
  };

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  // Simulator State
  const [selectedScenario, setSelectedScenario] = useState(MOCK_SCENARIOS[0]);
  const [simHistory, setSimHistory] = useState([]);
  const [simInput, setSimInput] = useState('');
  const [simAgitation, setSimAgitation] = useState(6);
  const [simTip, setSimTip] = useState(null);
  const [isSimLoading, setIsSimLoading] = useState(false);

  // RAG Search State
  const [ragQuery, setRagQuery] = useState('');
  const [ragResults, setRagResults] = useState([]);
  const [isSearchingRAG, setIsSearchingRAG] = useState(false);

  // Check backend health on load
  useEffect(() => {
    checkBackendHealth();
    loadPatientData();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/health`);
      if (res.ok) {
        setBackendStatus('online');
      } else {
        setBackendStatus('offline');
      }
    } catch {
      setBackendStatus('offline');
    }
  };

  const loadPatientData = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/patient`);
      if (res.ok) {
        const data = await res.json();
        setPatient(data);
      }
    } catch (e) {
      console.log('Error loading patient data, using fallback.', e);
    }
  };

  const seedDatabase = async () => {
    setIsSeeding(true);
    try {
      const res = await fetch(`${BACKEND_URL}/guidelines/seed`, { method: 'POST' });
      if (res.ok) {
        alert('Dementia care guidelines successfully seeded into vector database!');
      } else {
        alert('Failed to seed guidelines.');
      }
    } catch (e) {
      alert('Error connecting to backend: ' + e.message);
    } finally {
      setIsSeeding(false);
    }
  };

  // ----------------------------------------------------
  // Profile Editor Actions
  // ----------------------------------------------------
  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setIsSavingProfile(true);
    if (backendStatus === 'online') {
      try {
        const res = await fetch(`${BACKEND_URL}/patient`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(patient)
        });
        if (res.ok) {
          const data = await res.json();
          setPatient(data);
          alert('Patient profile saved to database!');
        }
      } catch (e) {
        alert('Failed to save to backend: ' + e.message);
      }
    } else {
      // Local save
      alert('Patient profile updated locally (Mock Mode)!');
    }
    setIsSavingProfile(false);
  };

  const handleAddTrigger = () => {
    if (newTrigger.trim() && !patient.triggers.includes(newTrigger.trim())) {
      setPatient({
        ...patient,
        triggers: [...patient.triggers, newTrigger.trim()]
      });
      setNewTrigger('');
    }
  };

  const handleRemoveTrigger = (index) => {
    const updated = [...patient.triggers];
    updated.splice(index, 1);
    setPatient({ ...patient, triggers: updated });
  };

  const handleAddPreference = () => {
    if (newPreference.trim() && !patient.preferences.includes(newPreference.trim())) {
      setPatient({
        ...patient,
        preferences: [...patient.preferences, newPreference.trim()]
      });
      setNewPreference('');
    }
  };

  const handleRemovePreference = (index) => {
    const updated = [...patient.preferences];
    updated.splice(index, 1);
    setPatient({ ...patient, preferences: updated });
  };

  // ----------------------------------------------------
  // Ingestion & 5-Agent Analysis Actions
  // ----------------------------------------------------
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setInputText('');
      if (fileUrl) {
        URL.revokeObjectURL(fileUrl);
      }
      setFileUrl(URL.createObjectURL(file));
    }
  };

  const simulateStepLoading = (step, callback) => {
    setAnalysisStep(step);
    setTimeout(callback, 800);
  };

  const handleAnalyze = async () => {
    if (!inputText.trim() && !selectedFile) return;
    setIsAnalyzing(true);
    setAnalysisResult(null);

    // 5-Agent Pipeline Visual Indicator Sequence
    simulateStepLoading(1, () => { // Interaction Analysis
      simulateStepLoading(2, () => { // Patient Context
        simulateStepLoading(3, () => { // Guideline RAG
          simulateStepLoading(4, () => { // Safety
            simulateStepLoading(5, async () => { // Coaching Synthesis
              if (backendStatus === 'online') {
                try {
                  let res;
                  if (selectedFile) {
                    const formData = new FormData();
                    formData.append('file', selectedFile);
                    res = await fetch(`${BACKEND_URL}/analyze/file`, {
                      method: 'POST',
                      body: formData
                    });
                  } else {
                    res = await fetch(`${BACKEND_URL}/analyze/text`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ description: inputText })
                    });
                  }

                  if (res.ok) {
                    const data = await res.json();
                    setAnalysisResult(data);
                  } else {
                    const err = await res.json();
                    alert('Error from API: ' + (err.detail || 'Unknown error'));
                    setAnalysisResult(MOCK_ANALYSIS_MED_REFUSAL); // Fallback on failure
                  }
                } catch (e) {
                  alert('Connection error, using mock data: ' + e.message);
                  setAnalysisResult(MOCK_ANALYSIS_MED_REFUSAL);
                }
              } else {
                // Offline Mock Mode
                setAnalysisResult(MOCK_ANALYSIS_MED_REFUSAL);
              }
              setIsAnalyzing(false);
              setAnalysisStep(0);
            });
          });
        });
      });
    });
  };

  // ----------------------------------------------------
  // Simulator Actions
  // ----------------------------------------------------
  const startSimulator = (scenario) => {
    setSelectedScenario(scenario);
    setSimAgitation(scenario.initial_agitation);
    setSimTip(null);
    setSimHistory([
      { role: "assistant", content: scenario.initial_dialogue }
    ]);
  };

  useEffect(() => {
    startSimulator(selectedScenario);
  }, [selectedScenario]);

  const handleSendSimMessage = async (e) => {
    e.preventDefault();
    if (!simInput.trim() || isSimLoading) return;

    const userMessage = { role: "user", content: simInput };
    const updatedHistory = [...simHistory, userMessage];
    setSimHistory(updatedHistory);
    setSimInput('');
    setIsSimLoading(true);

    if (backendStatus === 'online') {
      try {
        const res = await fetch(`${BACKEND_URL}/simulator/step`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            scenario: selectedScenario.title,
            chat_history: updatedHistory
          })
        });
        if (res.ok) {
          const data = await res.json();
          setSimHistory([...updatedHistory, { role: "assistant", content: data.patient_dialogue }]);
          setSimAgitation(data.patient_agitation_level);
          setSimTip(data.coaching_tip);
        } else {
          mockSimResponse(simInput, updatedHistory);
        }
      } catch {
        mockSimResponse(simInput, updatedHistory);
      } finally {
        setIsSimLoading(false);
      }
    } else {
      // Mock simulation logic
      setTimeout(() => {
        mockSimResponse(simInput, updatedHistory);
        setIsSimLoading(false);
      }, 1000);
    }
  };

  const mockSimResponse = (input, history) => {
    let responseText = "";
    let deltaAgitation = 0;
    let tip = "";
    const inputLower = input.toLowerCase();

    if (selectedScenario.id === 'med_refusal') {
      if (inputLower.includes('must') || inputLower.includes('have to') || inputLower.includes('wrong') || inputLower.includes('doctor')) {
        responseText = "I don't care what the doctor said! You're lying to me. You want me to sleep so you can search my room. Go away!";
        deltaAgitation = 2;
        tip = "Trap detected: Attempted to use logic/authority ('have to', 'doctor') which triggers paranoia. Try validating Maria's mistrust.";
      } else if (inputLower.includes('sorry') || inputLower.includes('tea') || inputLower.includes('cookies') || inputLower.includes('gardening') || inputLower.includes('band')) {
        responseText = "Well... I do like chamomile tea. But make sure you don't touch my papers in the living room. Where are my gardening magazines?";
        deltaAgitation = -2;
        tip = "Success: You validated her distraction or offered a preferred comfort (tea/gardening). Agitation decreases.";
      } else {
        responseText = "Leave me alone! Why are you standing there holding that bottle? It looks toxic!";
        deltaAgitation = 0;
        tip = "Tip: Put the pills away. Focus on validation therapy (agree with her feelings) or redirection.";
      }
    } else if (selectedScenario.id === 'shower_refusal') {
      if (inputLower.includes('dirty') || inputLower.includes('smell') || inputLower.includes('showered') || inputLower.includes('yesterday')) {
        responseText = "I do NOT smell! You are insulting me in my own house. I'm not going in that bathroom, it's freezing!";
        deltaAgitation = 2;
        tip = "Trap detected: Correcting her memory ('yesterday') or accusing her of smelling triggers shame. Validate that she feels clean, or check room comfort.";
      } else if (inputLower.includes('warm') || inputLower.includes('towel') || inputLower.includes('music') || inputLower.includes('comfortable')) {
        responseText = "Warm towels? Well, it is a bit drafty in here. I suppose you can turn the heater on first. But don't rush me.";
        deltaAgitation = -1;
        tip = "Success: Addressing environment warmth and dignity helps lower resistance to bathing.";
      } else {
        responseText = "I said no! Why are you always bossing me around like a child?";
        deltaAgitation = 1;
        tip = "Tip: Try making it about comfort. Use Teepa Snow's positive physical approach: 'Let's get you warmed up first.'";
      }
    } else {
      // wants to go home
      if (inputLower.includes('dead') || inputLower.includes('sold') || inputLower.includes('here') || inputLower.includes('can\'t')) {
        responseText = "No, you're wrong! My mother is waiting! Why are you keeping me locked up here? Help! Someone help me!";
        deltaAgitation = 3;
        tip = "Critical Trap: Reality orientation (telling her her mother is dead or house is sold) triggers traumatic grief. Validate her memory instead.";
      } else if (inputLower.includes('tell me') || inputLower.includes('mother') || inputLower.includes('farm') || inputLower.includes('childhood')) {
        responseText = "My mother... she always made the best apple pies on Sundays. The farm had three horses... one was named Barnaby.";
        deltaAgitation = -2;
        tip = "Success: Validation therapy. By asking her to share a memory about her mother/farm, you validated her emotions and can now redirect her.";
      } else {
        responseText = "Get out of my way, I need to walk to the bus stop. The bus comes at 5:00!";
        deltaAgitation = 1;
        tip = "Tip: Ask about her home or childhood. Try: 'You really want to help your mom. Tell me about the chores you did.'"
      }
    }

    const newAgitation = Math.max(1, Math.min(10, simAgitation + deltaAgitation));
    setSimAgitation(newAgitation);
    setSimTip(tip);
    setSimHistory([...history, { role: "assistant", content: responseText }]);
  };

  // ----------------------------------------------------
  // RAG guidelines Search Actions
  // ----------------------------------------------------
  const handleRAGSearch = async (e) => {
    e.preventDefault();
    if (!ragQuery.trim()) return;
    setIsSearchingRAG(true);

    if (backendStatus === 'online') {
      try {
        const res = await fetch(`${BACKEND_URL}/analyze/text`, { // using text endpoint to get RAG feedback
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ description: ragQuery })
        });
        if (res.ok) {
          const data = await res.json();
          // Simulating extraction of RAG results
          setRagResults([
            {
              title: data.recommendations[0]?.strategy_name || "Care Protocol",
              category: "Intervention",
              text: data.recommendations[0]?.description || "No records match.",
            }
          ]);
        }
      } catch (e) {
        console.error("RAG search failed, using fallback.", e);
        mockRAGSearch(ragQuery);
      } finally {
        setIsSearchingRAG(false);
      }
    } else {
      setTimeout(() => {
        mockRAGSearch(ragQuery);
        setIsSearchingRAG(false);
      }, 600);
    }
  };

  const mockRAGSearch = (query) => {
    const q = query.toLowerCase();
    const defaults = [
      {
        title: "Handling Medication Refusal",
        category: "Medication Management",
        text: "When a dementia patient refuses medication, never argue or force. Validate feelings: 'I understand you are tired of pills.' Redirect attention: pair pills with applesauce, a cookie, or chamomile tea. Avoid saying 'the doctor ordered it'."
      },
      {
        title: "Managing Agitation and Resistance during Personal Care",
        category: "Activities of Daily Living (ADLs)",
        text: "Resistance to bathing is caused by feeling cold, exposed, or disoriented. Warm the room, cover shoulders, use Teepa Snow's Positive Physical Approach: approach from front, handshake grip, stand at side, low tone."
      },
      {
        title: "Responding to Repetitive Questions and Wanting to Go Home",
        category: "Emotional Distress",
        text: "Do not correct or tell them relatives are deceased. Use Validation Therapy to address emotional triggers: 'You are thinking of home. Tell me about your childhood home.' Redirect to laundry folding or tea."
      },
      {
        title: "Sundowning and Afternoon Pacing Management",
        category: "Behavioral Disturbances",
        text: "Sundowning refers to increased late-afternoon confusion. Reduce sensory overload: turn off loud TVs, dim lights, close blinds to block scary shadows. Keep environment peaceful."
      }
    ];

    const filtered = defaults.filter(d =>
      d.title.toLowerCase().includes(q) ||
      d.text.toLowerCase().includes(q) ||
      d.category.toLowerCase().includes(q)
    );

    setRagResults(filtered.length > 0 ? filtered : [
      {
        title: "Dementia Communication Guidelines",
        category: "General Practice",
        text: "Standard protocol is validation over correction. Agree with their emotional state, step back if combative, utilize physical comforts (blankets, familiar tunes), and use simplified, single-step prompts."
      }
    ]);
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="logo-container">
          <Activity className="logo-icon" size={32} />
          <div>
            <h1 className="logo-title">DementiaCare Coach</h1>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>AI-Powered Caregiver Co-Pilot</p>
          </div>
        </div>

        <div className="header-session-info" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginRight: 'auto', marginLeft: '2rem' }}>
          <div style={{ fontSize: '0.85rem', borderLeft: '1px solid var(--border-color)', paddingLeft: '1.5rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Patient: </span>
              <strong style={{ color: 'var(--text-main)' }}>{patient.name}</strong>
            </div>
            <div>
              <span style={{ color: 'var(--text-muted)' }}>Role: </span>
              <strong style={{ color: 'var(--text-main)' }}>Primary Caregiver (Daughter)</strong>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            onClick={toggleTheme}
            className="theme-toggle-btn"
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '0.5rem',
              borderRadius: '8px',
              color: 'var(--text-muted)',
              transition: 'all 0.2s ease'
            }}
          >
            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
          </button>

          <div className="api-status">
            <span className={`status-dot ${backendStatus === 'online' ? 'online' : backendStatus === 'offline' ? 'offline' : ''}`}></span>
            <span>Care Coach: {backendStatus.toUpperCase()}</span>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <nav className="tab-navigation">
        <button
          className={`tab-button ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <Activity size={18} />
          <span>Interaction Coach</span>
        </button>
        <button
          className={`tab-button ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          <User size={18} />
          <span>Patient Profile</span>
        </button>
        <button
          className={`tab-button ${activeTab === 'simulator' ? 'active' : ''}`}
          onClick={() => setActiveTab('simulator')}
        >
          <Gamepad2 size={18} />
          <span>Care Simulator</span>
        </button>
        <button
          className={`tab-button ${activeTab === 'guidelines' ? 'active' : ''}`}
          onClick={() => setActiveTab('guidelines')}
        >
          <BookOpen size={18} />
          <span>Care Guidelines</span>
        </button>
      </nav>

      {/* MAIN CONTAINER */}
      <main className="fade-in">
        {/* ==================================================== */}
        {/* TAB 1: COACHING DASHBOARD & ANALYSIS */}
        {/* ==================================================== */}
        {activeTab === 'dashboard' && (
          <div className="dashboard-grid split">
            {/* Left Column: Upload / Log Input */}
            <div className="glass-card">
              <h2 className="card-title">
                <Upload size={20} className="logo-icon" />
                Record Interaction
              </h2>

              <div className="form-group">
                <label className="form-label">Option A: Record or Upload Interaction</label>

                {showRecorder ? (
                  <div className="recorder-container">
                    <div className="recorder-header">
                      <div className="recording-status">
                        <span className={`status-dot ${isRecording ? 'online blink' : ''}`} style={{ backgroundColor: '#ef4444' }}></span>
                        <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>
                          {isRecording ? `Recording ${recordingType}...` : 'Ready to Record'}
                        </span>
                      </div>
                      <span className="recording-timer">{formatTime(recordingTime)}</span>
                    </div>

                    {recordingType === 'video' && (
                      <div className="webcam-preview-box">
                        <video ref={videoPreviewRef} autoPlay playsInline muted className="webcam-video" />
                      </div>
                    )}

                    {recordingType === 'audio' && (
                      <div className="audio-recording-box">
                        <Mic size={32} className={isRecording ? 'pulse' : ''} style={{ color: 'var(--primary)' }} />
                        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                          {isRecording ? 'Recording audio through microphone...' : 'Microphone ready.'}
                        </span>
                      </div>
                    )}

                    <div className="recorder-controls">
                      {!isRecording ? (
                        <button
                          type="button"
                          className="btn btn-primary"
                          onClick={() => startRecording(recordingType)}
                        >
                          <Circle size={14} fill="#ef4444" style={{ color: '#ef4444', marginRight: '0.25rem' }} />
                          Start
                        </button>
                      ) : (
                        <button
                          type="button"
                          className="btn btn-danger"
                          onClick={stopRecording}
                          style={{ backgroundColor: 'var(--color-danger)', borderColor: 'var(--color-danger)' }}
                        >
                          <Square size={14} fill="#fff" style={{ marginRight: '0.25rem' }} />
                          Stop & Use
                        </button>
                      )}
                      <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={() => { cleanupRecording(); setShowRecorder(false); }}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div
                      className="upload-dropzone"
                      onClick={() => document.getElementById('file-upload').click()}
                    >
                      <Upload size={32} style={{ color: 'var(--primary)' }} />
                      <p style={{ fontSize: '0.9rem', fontWeight: 600 }}>Drag file here or click to browse</p>
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Supports MP4, MOV, MP3, WAV</p>
                    </div>

                    <div className="record-actions-row">
                      <button
                        type="button"
                        className="btn btn-secondary btn-sm"
                        onClick={() => { setShowRecorder(true); startRecording('video'); }}
                        style={{ flex: 1 }}
                      >
                        <Video size={14} style={{ marginRight: '0.4rem' }} />
                        Record Video
                      </button>
                      <button
                        type="button"
                        className="btn btn-secondary btn-sm"
                        onClick={() => { setShowRecorder(true); startRecording('audio'); }}
                        style={{ flex: 1 }}
                      >
                        <Mic size={14} style={{ marginRight: '0.4rem' }} />
                        Record Audio
                      </button>
                    </div>
                  </>
                )}

                <input
                  type="file"
                  id="file-upload"
                  style={{ display: 'none' }}
                  onChange={handleFileChange}
                  accept="video/*,audio/*"
                />

                {selectedFile && !showRecorder && (
                  <div className="media-preview-card">
                    <div className="media-preview-header">
                      <div className="media-preview-info">
                        <Activity size={14} style={{ color: 'var(--primary)', flexShrink: 0 }} />
                        <span className="media-preview-title" title={selectedFile.name}>{selectedFile.name}</span>
                      </div>
                      <button
                        type="button"
                        className="tag-delete-btn"
                        onClick={() => { setSelectedFile(null); setFileUrl(null); }}
                        style={{ padding: '0.25rem' }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                    <div className="media-player-wrapper">
                      {selectedFile.type.startsWith('video/') || selectedFile.name.endsWith('.webm') || selectedFile.name.endsWith('.mp4') || selectedFile.name.endsWith('.mov') ? (
                        <video className="media-player" src={fileUrl} controls playsInline />
                      ) : selectedFile.type.startsWith('audio/') || selectedFile.name.endsWith('.mp3') || selectedFile.name.endsWith('.wav') || selectedFile.name.endsWith('.weba') ? (
                        <audio className="media-player audio" src={fileUrl} controls />
                      ) : (
                        <div className="generic-file-preview">
                          <Activity size={24} />
                          <span>File ready for upload</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>— OR —</span>
              </div>

              <div className="form-group">
                <label className="form-label">Option B: Describe the Interaction (Text)</label>
                <textarea
                  className="form-textarea"
                  rows={6}
                  placeholder="Example: Mom got agitated when I showed her her heart pill. She accused me of stealing and yelled that she wouldn't take it. I showed her the medicine bottle and told her she was wrong, which made her shout louder..."
                  value={inputText}
                  onChange={(e) => {
                    setInputText(e.target.value);
                    setSelectedFile(null);
                  }}
                ></textarea>
              </div>

              <button
                className="btn btn-primary"
                onClick={handleAnalyze}
                disabled={isAnalyzing || (!inputText.trim() && !selectedFile)}
              >
                {isAnalyzing ? (
                  <>
                    <RefreshCw className="spinner" size={16} />
                    <span>Analyzing Interaction...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={16} />
                    <span>Analyze Care Interaction</span>
                  </>
                )}
              </button>

              {/* Analysis Steps Visualizer */}
              {isAnalyzing && (
                <div className="pipeline-status">
                  <p style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary)' }}>Coaching Analysis Sequence:</p>

                  <div className={`pipeline-step ${analysisStep === 1 ? 'active' : analysisStep > 1 ? 'completed' : ''}`}>
                    {analysisStep === 1 ? <div className="spinner" /> : <CheckCircle2 size={14} />}
                    <span>Step 1: Identifying verbal & non-verbal interaction cues</span>
                  </div>

                  <div className={`pipeline-step ${analysisStep === 2 ? 'active' : analysisStep > 2 ? 'completed' : ''}`}>
                    {analysisStep === 2 ? <div className="spinner" /> : <CheckCircle2 size={14} />}
                    <span>Step 2: Checking patient context (schedule & triggers)</span>
                  </div>

                  <div className={`pipeline-step ${analysisStep === 3 ? 'active' : analysisStep > 3 ? 'completed' : ''}`}>
                    {analysisStep === 3 ? <div className="spinner" /> : <CheckCircle2 size={14} />}
                    <span>Step 3: Referencing clinical care guidelines</span>
                  </div>

                  <div className={`pipeline-step ${analysisStep === 4 ? 'active' : analysisStep > 4 ? 'completed' : ''}`}>
                    {analysisStep === 4 ? <div className="spinner" /> : <CheckCircle2 size={14} />}
                    <span>Step 4: Assessing safety & medical risks</span>
                  </div>

                  <div className={`pipeline-step ${analysisStep === 5 ? 'active' : ''}`}>
                    {analysisStep === 5 ? <div className="spinner" /> : <CheckCircle2 size={14} />}
                    <span>Step 5: Synthesizing caregiver coaching plan</span>
                  </div>
                </div>
              )}
            </div>

            {/* Right Column: Coaching Results */}
            <div className="glass-card">
              <h2 className="card-title">
                <Sparkles size={20} className="logo-icon" />
                Coaching Feedback
              </h2>

              {!analysisResult && !isAnalyzing && (
                <div style={{ textAlign: 'center', padding: '4rem 1.5rem', color: 'var(--text-muted)' }}>
                  <Activity size={48} style={{ opacity: 0.2, margin: '0 auto 1rem' }} />
                  <p style={{ fontWeight: 500 }}>No analysis loaded.</p>
                  <p style={{ fontSize: '0.85rem', marginTop: '0.25rem' }}>Upload a recording or type a text log, then run the analysis engine to receive coaching recommendations.</p>
                </div>
              )}

              {isAnalyzing && (
                <div style={{ textAlign: 'center', padding: '6rem 1.5rem', color: 'var(--text-muted)' }}>
                  <RefreshCw className="spinner" size={32} style={{ margin: '0 auto 1.5rem' }} />
                  <p style={{ fontWeight: 600, color: 'var(--text-main)' }}>Analyzing Care Interaction...</p>
                  <p style={{ fontSize: '0.85rem', marginTop: '0.25rem' }}>Evaluating verbal tone, clinical context, care guidelines, and safety hazards.</p>
                </div>
              )}

              {analysisResult && !isAnalyzing && (
                <div className="feedback-grid fade-in">

                  {/* Summary & Behavior Recognition */}
                  <div className="glass-card feedback-full-width" style={{ background: 'var(--card-inner-bg)', gap: '0.75rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span className="api-status" style={{ background: 'var(--primary-glow)', border: '1px solid var(--primary)' }}>
                        <Smile size={14} style={{ color: 'var(--primary)' }} />
                        <span style={{ color: 'var(--primary)', fontWeight: 600 }}>Behavioral Analysis</span>
                      </span>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Patient Emotion: <strong>{analysisResult.behavior_analysis.patient_emotion}</strong></span>
                    </div>
                    <p style={{ fontSize: '0.95rem', fontStyle: 'italic', color: 'var(--text-light)' }}>
                      "{analysisResult.behavior_analysis.interaction_summary}"
                    </p>

                    <div className="analysis-score-container" style={{ marginTop: '0.5rem' }}>
                      <div className="score-box">
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Patient Triggers</p>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', justifyContent: 'center', marginTop: '0.35rem' }}>
                          {analysisResult.behavior_analysis.patient_triggers.map((t, idx) => (
                            <span key={idx} className="tag-pill" style={{ fontSize: '0.75rem', padding: '0.15rem 0.4rem' }}>{t}</span>
                          ))}
                        </div>
                      </div>
                      <div className="score-box">
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Caregiver Style</p>
                        <p style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--primary)', marginTop: '0.35rem' }}>
                          {analysisResult.behavior_analysis.caregiver_communication_style}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Safety / Escalation Flags */}
                  {analysisResult.clinical_safety_flags && analysisResult.clinical_safety_flags.length > 0 && (
                    <div className="feedback-full-width alert-box danger">
                      <AlertTriangle size={24} style={{ flexShrink: 0 }} />
                      <div>
                        <p style={{ fontWeight: 700, fontSize: '0.9rem' }}>CRITICAL CLINICAL & SAFETY ALERTS</p>
                        <ul style={{ paddingLeft: '1.2rem', marginTop: '0.25rem', fontSize: '0.85rem' }}>
                          {analysisResult.clinical_safety_flags.map((flag, idx) => (
                            <li key={idx}>{flag}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}

                  {/* Clinical Behavioral Timeline (Behavioral Coding Worksheet) */}
                  {analysisResult.behavioral_timeline && analysisResult.behavioral_timeline.length > 0 && (
                    <div className="glass-card feedback-full-width" style={{ background: 'var(--card-inner-bg)', gap: '1rem', border: '1px solid var(--border-color)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                        <Activity size={18} style={{ color: 'var(--primary)' }} />
                        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: 'var(--text-main)', margin: 0 }}>
                          Clinical Behavioral Timeline
                        </h3>
                        <span style={{ fontSize: '0.75rem', color: 'var(--primary)', marginLeft: 'auto', background: 'var(--primary-glow)', border: '1px solid var(--primary)', padding: '0.2rem 0.5rem', borderRadius: '4px', fontWeight: 600 }}>
                          Behavioral Coding Worksheet
                        </span>
                      </div>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                        Chronological mapping of specific timeframes to observable patient behaviors, clinical symptoms, and underlying cognitive or emotional states.
                      </p>
                      <div style={{ overflowX: 'auto', marginTop: '0.5rem' }}>
                        <table className="timeline-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
                          <thead>
                            <tr style={{ borderBottom: '2px solid var(--border-color)', color: 'var(--text-muted)' }}>
                              <th style={{ padding: '0.6rem 0.8rem', fontWeight: 600, width: '120px' }}>Timeframe</th>
                              <th style={{ padding: '0.6rem 0.8rem', fontWeight: 600 }}>Observable Behavior / Speech</th>
                              <th style={{ padding: '0.6rem 0.8rem', fontWeight: 600, width: '220px' }}>Clinical Symptom Term</th>
                              <th style={{ padding: '0.6rem 0.8rem', fontWeight: 600 }}>Underlying Emotion / Cognitive State</th>
                            </tr>
                          </thead>
                          <tbody>
                            {analysisResult.behavioral_timeline.map((obs, idx) => (
                              <tr key={idx} style={{ borderBottom: '1px solid var(--border-color)', verticalAlign: 'top' }}>
                                <td style={{ padding: '0.8rem' }}>
                                  <span className="tag-pill" style={{ background: 'var(--primary-glow)', border: '1px solid var(--primary)', color: 'var(--primary)', fontWeight: 600, display: 'inline-block', fontSize: '0.8rem' }}>
                                    {obs.timeframe}
                                  </span>
                                </td>
                                <td style={{ padding: '0.8rem', color: 'var(--text-light)', lineHeight: '1.4' }}>
                                  {obs.observable_behavior}
                                </td>
                                <td style={{ padding: '0.8rem' }}>
                                  <span style={{
                                    background: 'var(--symptom-tag-bg)',
                                    border: '1px solid var(--symptom-tag-border)',
                                    color: 'var(--symptom-tag-color)',
                                    fontSize: '0.8rem',
                                    padding: '0.15rem 0.4rem',
                                    borderRadius: '4px',
                                    fontWeight: 500,
                                    display: 'inline-block'
                                  }}>
                                    {obs.clinical_symptom}
                                  </span>
                                </td>
                                <td style={{ padding: '0.8rem', color: 'var(--text-muted)', fontSize: '0.85rem', fontStyle: 'italic', lineHeight: '1.4' }}>
                                  {obs.cognitive_state}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* Strengths */}
                  <div className="glass-card" style={{ gap: '0.75rem' }}>
                    <h3 style={{ fontSize: '1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-success)' }}>
                      <ThumbsUp size={16} />
                      Caregiver Strengths
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {analysisResult.strengths.map((str, idx) => (
                        <div key={idx} className="check-item success">
                          <CheckCircle2 size={16} />
                          <span>{str}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Opportunities */}
                  <div className="glass-card" style={{ gap: '0.75rem' }}>
                    <h3 style={{ fontSize: '1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-warning)' }}>
                      <AlertTriangle size={16} />
                      Opportunities to Improve
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {analysisResult.opportunities_for_improvement.map((opp, idx) => (
                        <div key={idx} className="check-item opportunity">
                          <AlertTriangle size={16} />
                          <span>{opp}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Dialogue Coaching Scripts */}
                  <div className="glass-card feedback-full-width" style={{ gap: '0.75rem' }}>
                    <h3 style={{ fontSize: '1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--secondary)' }}>
                      <MessageSquare size={16} />
                      Recommended Dialogue Scripts (What to say)
                    </h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1rem' }}>
                      {/* We chunk scripts into pairs */}
                      {analysisResult.coaching_scripts.map((script, idx) => {
                        const isAvoid = script.startsWith("Avoid saying:");
                        return (
                          <div key={idx} className={`dialogue-line ${isAvoid ? 'avoid' : 'try'}`}>
                            <strong>{isAvoid ? 'AVOID:' : 'TRY SAYING:'}</strong> {script.replace("Avoid saying:", "").replace("Try saying:", "")}
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Clinical Recommendations */}
                  <div className="feedback-full-width" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '0.5rem' }}>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 600, borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
                      Clinical Care Protocols
                    </h3>

                    {analysisResult.recommendations.map((rec, idx) => (
                      <div key={idx} className="glass-card" style={{ background: 'var(--secondary-glow-bg)', border: '1px solid var(--secondary-glow-border)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontWeight: 700, color: 'var(--secondary)' }}>{rec.strategy_name}</span>
                          <span className="api-status" style={{ fontSize: '0.75rem', padding: '0.15rem 0.5rem' }}>Grounded Advice</span>
                        </div>
                        <p style={{ fontSize: '0.9rem', color: 'var(--text-light)' }}>{rec.description}</p>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', borderTop: '1px dashed var(--border-color)', paddingTop: '0.5rem' }}>
                          <strong>Why this works:</strong> {rec.rationality}
                        </p>
                      </div>
                    ))}
                  </div>

                </div>
              )}
            </div>
          </div>
        )}

        {/* ==================================================== */}
        {/* TAB 2: PATIENT PROFILE EDITOR */}
        {/* ==================================================== */}
        {activeTab === 'profile' && (
          <div className="glass-card" style={{ maxWidth: '800px', margin: '0 auto' }}>
            <h2 className="card-title">
              <User size={20} className="logo-icon" />
              Patient Profile Context
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Maintain accurate background details. The AI agent consults this profile during analysis to ensure coaching advice aligns with physical capability and medical records.
            </p>

            <form onSubmit={handleSaveProfile} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label">Patient Name</label>
                  <input
                    type="text"
                    className="form-input"
                    value={patient.name}
                    onChange={(e) => setPatient({ ...patient, name: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Dementia Stage / Type</label>
                  <input
                    type="text"
                    className="form-input"
                    value={patient.dementia_type}
                    onChange={(e) => setPatient({ ...patient, dementia_type: e.target.value })}
                    required
                  />
                </div>
              </div>

              {/* Triggers */}
              <div className="form-group">
                <label className="form-label">Known Behavioral Triggers (E.g. direct correction)</label>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <input
                    type="text"
                    className="form-input"
                    style={{ flex: 1 }}
                    placeholder="E.g., being rushed, loud voices"
                    value={newTrigger}
                    onChange={(e) => setNewTrigger(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTrigger())}
                  />
                  <button type="button" className="btn btn-secondary" onClick={handleAddTrigger}>
                    <Plus size={18} />
                  </button>
                </div>
                <div className="tag-container">
                  {patient.triggers.map((t, idx) => (
                    <div key={idx} className="tag-pill">
                      <span>{t}</span>
                      <button type="button" className="tag-delete-btn" onClick={() => handleRemoveTrigger(idx)}>
                        <Trash2 size={12} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Preferences */}
              <div className="form-group">
                <label className="form-label">Comfort items, routines & preferences</label>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <input
                    type="text"
                    className="form-input"
                    style={{ flex: 1 }}
                    placeholder="E.g., 1950s big band music, warm cider"
                    value={newPreference}
                    onChange={(e) => setNewPreference(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddPreference())}
                  />
                  <button type="button" className="btn btn-secondary" onClick={handleAddPreference}>
                    <Plus size={18} />
                  </button>
                </div>
                <div className="tag-container">
                  {patient.preferences.map((p, idx) => (
                    <div key={idx} className="tag-pill" style={{ borderColor: 'var(--preference-tag-border)', color: 'var(--preference-tag-color)' }}>
                      <span>{p}</span>
                      <button type="button" className="tag-delete-btn" onClick={() => handleRemovePreference(idx)}>
                        <Trash2 size={12} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Background / History */}
              <div className="form-group">
                <label className="form-label">Clinical Background, Trauma History & Daily Challenges</label>
                <textarea
                  className="form-textarea"
                  rows={5}
                  value={patient.background}
                  onChange={(e) => setPatient({ ...patient, background: e.target.value })}
                  placeholder="Detail daily habits, mobility level, medication compliance history, and any clinical diagnoses (diabetes, neuropathy) to ensure safety agent audits are valid."
                ></textarea>
              </div>

              <button type="submit" className="btn btn-primary" disabled={isSavingProfile}>
                {isSavingProfile ? 'Saving...' : 'Save Patient Profile'}
              </button>
            </form>
          </div>
        )}

        {/* ==================================================== */}
        {/* TAB 3: INTERACTIVE SIMULATOR */}
        {/* ==================================================== */}
        {activeTab === 'simulator' && (
          <div className="dashboard-grid split">
            {/* Scenario Chooser */}
            <div className="glass-card">
              <h2 className="card-title">
                <Gamepad2 size={20} className="logo-icon" />
                Practice Scenarios
              </h2>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Select a scenario. The simulated patient agent (Maria) will respond realistically. Practice validation therapy and redirection to keep her agitation low.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {MOCK_SCENARIOS.map((scen) => (
                  <div
                    key={scen.id}
                    className={`glass-card ${selectedScenario.id === scen.id ? 'active' : ''}`}
                    style={{
                      padding: '1rem',
                      cursor: 'pointer',
                      background: selectedScenario.id === scen.id ? 'rgba(6, 182, 212, 0.08)' : 'var(--bg-card)',
                      borderColor: selectedScenario.id === scen.id ? 'var(--primary)' : 'var(--border-color)'
                    }}
                    onClick={() => setSelectedScenario(scen)}
                  >
                    <p style={{ fontWeight: 700, fontSize: '0.95rem', color: selectedScenario.id === scen.id ? 'var(--primary)' : 'var(--text-main)' }}>
                      {scen.title}
                    </p>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                      {scen.description}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Chat Room */}
            <div className="glass-card simulator-panel">
              <div className="simulator-header">
                <div>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Training Chat with Maria</h3>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Scenario: {selectedScenario.title}</p>
                </div>

                {/* Agitation Score Meter */}
                <div className="agitation-meter-wrapper">
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>Maria's Agitation:</span>
                  <span style={{ fontWeight: 800, color: simAgitation > 7 ? 'var(--color-danger)' : simAgitation > 4 ? 'var(--color-warning)' : 'var(--color-success)' }}>
                    {simAgitation}/10
                  </span>
                  <div className="agitation-bar-container">
                    <div
                      className="agitation-bar-fill"
                      style={{
                        width: `${simAgitation * 10}%`,
                        backgroundColor: simAgitation > 7 ? 'var(--color-danger)' : simAgitation > 4 ? 'var(--color-warning)' : 'var(--color-success)'
                      }}
                    ></div>
                  </div>
                </div>
              </div>

              {/* Chat Bubble History */}
              <div className="chat-history">
                {simHistory.map((msg, index) => (
                  <div
                    key={index}
                    className={`chat-bubble ${msg.role === 'user' ? 'caregiver' : 'patient'}`}
                  >
                    {msg.content}
                  </div>
                ))}

                {isSimLoading && (
                  <div className="chat-bubble patient" style={{ opacity: 0.6 }}>
                    <RefreshCw className="spinner" size={14} style={{ display: 'inline-block', marginRight: '0.5rem' }} />
                    Maria is thinking...
                  </div>
                )}

                {/* Hidden Coaching Tip Popover */}
                {simTip && !isSimLoading && (
                  <div className="coaching-toast">
                    <Info size={16} style={{ flexShrink: 0, color: '#818cf8' }} />
                    <span>{simTip}</span>
                  </div>
                )}
              </div>

              {/* Input Message Form */}
              <form onSubmit={handleSendSimMessage} className="chat-input-area">
                <input
                  type="text"
                  className="form-input"
                  style={{ flex: 1 }}
                  placeholder="Type your response to Maria..."
                  value={simInput}
                  onChange={(e) => setSimInput(e.target.value)}
                  disabled={isSimLoading}
                />
                <button type="submit" className="btn btn-primary" disabled={isSimLoading || !simInput.trim()}>
                  Send
                </button>
              </form>
            </div>
          </div>
        )}

        {/* ==================================================== */}
        {/* TAB 4: CLINICAL GUIDELINES RAG */}
        {/* ==================================================== */}
        {activeTab === 'guidelines' && (
          <div className="glass-card" style={{ maxWidth: '900px', margin: '0 auto' }}>
            <h2 className="card-title">
              <BookOpen size={20} className="logo-icon" />
              Care Guidelines Library
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Search the database of dementia care guidelines. The system uses these guidelines to retrieve verified caregiver coaching protocols.
            </p>

            <form onSubmit={handleRAGSearch} style={{ display: 'flex', gap: '0.5rem', margin: '1rem 0' }}>
              <input
                type="text"
                className="form-input"
                style={{ flex: 1 }}
                placeholder="Search database: e.g. medication refusal, bathing resistance, validation therapy..."
                value={ragQuery}
                onChange={(e) => setRagQuery(e.target.value)}
              />
              <button type="submit" className="btn btn-primary">
                <Search size={18} />
                Search
              </button>
            </form>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1.5rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', color: 'var(--primary)' }}>
                {ragResults.length > 0 ? 'Search Results' : 'Verified Dementia Care Guidelines'}
              </h3>

              {isSearchingRAG ? (
                <div style={{ textAlign: 'center', padding: '2rem' }}>
                  <RefreshCw className="spinner" size={24} style={{ margin: '0 auto' }} />
                </div>
              ) : (
                <>
                  {(ragResults.length > 0 ? ragResults : [
                    {
                      title: "Handling Medication Refusal",
                      category: "Medication Management",
                      text: "When a dementia patient refuses medication, never argue, force, or lecture them. Instead, validate their feelings by saying: 'I understand you're tired of taking these pills, they do look big.' Redirect their attention to a pleasant topic or routine. Pair medication with a treat or favorite food: 'Let's have a cookie first, then we can take this to help you feel strong.' Avoid logical explanations or saying 'the doctor ordered it', as logic often escalates agitation in dementia."
                    },
                    {
                      title: "Managing Agitation and Resistance during Personal Care",
                      category: "Activities of Daily Living (ADLs)",
                      text: "Resistance to bathing or dressing is often caused by feeling cold, exposed, or confused. Keep the environment warm, drape a towel over their shoulders for privacy, and explain each step in simple, positive words. Use Teepa Snow's Positive Physical Approach: approach from the front, call their name, slide hand into a hand-shake grip, stand at their side (not directly in front, which is confrontational), and speak in a low, gentle voice. If they become aggressive, step back to give them personal space. Never force care; stop and try again in 15 minutes."
                    },
                    {
                      title: "Responding to Repetitive Questions and Wanting to Go Home",
                      category: "Emotional Distress",
                      text: "When a patient repeatedly asks to 'go home' or asks for a deceased relative, do not correct them or tell them their parents are dead. This causes fresh grief and distress. Instead, use Validation Therapy to address the emotional need behind the words. Say: 'You are thinking about home/your mom. Tell me about your childhood home.' or 'What did you like to cook with your mom?' Once they are engaged in sharing memories, transition/redirect their attention to a comforting current activity: 'That sounds beautiful. Let's have a cup of warm tea while we fold these towels.'"
                    },
                    {
                      title: "Sundowning and Afternoon Pacing Management",
                      category: "Behavioral Disturbances",
                      text: "Sundowning refers to increased confusion, pacing, and anxiety in the late afternoon or early evening. To manage this, reduce sensory stimulation: turn off noisy TVs, dim bright overhead lights, and close blinds to prevent shadows which patients may interpret as intruders. Keep the environment calm. Ensure adequate, soft lighting to prevent falls and confusion. Engage the patient in soothing, structured activities in the early afternoon (like folding laundry, listening to soft music, or sorting buttons) to prevent late-day energy spikes."
                    }
                  ]).map((doc, idx) => (
                    <div key={idx} className="glass-card" style={{ padding: '1.25rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <h4 style={{ fontWeight: 700, color: 'var(--text-main)' }}>{doc.title}</h4>
                        <span className="api-status" style={{ fontSize: '0.75rem', padding: '0.15rem 0.5rem', background: 'var(--secondary-glow)', color: 'var(--preference-tag-color)', border: '1px solid var(--preference-tag-border)' }}>
                          {doc.category}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.9rem', color: 'var(--text-light)', marginTop: '0.5rem', lineHeight: '1.5' }}>
                        {doc.text}
                      </p>
                    </div>
                  ))}
                </>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
