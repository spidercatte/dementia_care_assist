import React, { useState, useEffect } from 'react';
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
  Clock
} from 'lucide-react';

const BACKEND_URL = 'http://localhost:8000';

// Mock data fallbacks for demonstration when backend is offline
const MOCK_PATIENT = {
  name: "Arthur",
  dementia_type: "Alzheimer's (Moderate Stage)",
  triggers: ["direct correction", "being rushed", "loud noises", "asking 'do you remember?'"],
  preferences: ["listening to 1950s big band music", "drinking chamomile tea", "talking about his past work as a carpenter"],
  background: "Arthur is 78 years old. He lives at home with his daughter who is his primary caregiver. He often gets confused in the late afternoon (sundowning) and can refuse medication or personal care because he believes he has to go to work or that his daughter is trying to poison him."
};

const MOCK_ANALYSIS_MED_REFUSAL = {
  behavior_analysis: {
    patient_emotion: "agitated and suspicious",
    patient_triggers: ["direct correction ('you must take this now')", "rushing"],
    caregiver_communication_style: "impatient, lecturing, correcting Arthur's timeline",
    interaction_summary: "Arthur refused to take his afternoon heart medication, stating that he had already taken it and that his caregiver was trying to steal his money. The caregiver argued back, telling him he was wrong and showing him the pill bottle to 'prove' he hadn't taken it, which escalated Arthur's shouting."
  },
  strengths: [
    "Caregiver kept their voice volume relatively stable initially.",
    "Did not touch or physically force the patient."
  ],
  opportunities_for_improvement: [
    "Tried to use logic to 'prove' Arthur was wrong (showing the pill bottle).",
    "Directly corrected him ('No you didn't, Dad'), which triggered defensiveness.",
    "Argued about the money accusation, causing further escalation."
  ],
  clinical_safety_flags: [
    "Potential cardiovascular medication omission risk. If missed repeatedly for >48 hours, contact cardiologist."
  ],
  coaching_scripts: [
    "Avoid saying: 'Dad, you didn't take your pills! Stop lying, I have the bottle right here.'",
    "Try saying: 'I see you're worried about these pills, Dad. They do look different today. Let's set them aside and have a cup of your favorite tea first.'",
    "Avoid saying: 'I'm not stealing your money, I'm your daughter!'",
    "Try saying: 'You want to make sure your money is safe. I'll make sure everything is locked in the drawer. Let's look at your carpentry magazines.'"
  ],
  recommendations: [
    {
      strategy_name: "Validation Therapy",
      description: "Acknowledge Arthur's feeling of fear or mistrust instead of debating the facts. Say: 'You want to be sure you are safe, and I want that too.'",
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
    description: "Arthur refuses his heart medication, insisting he already took it and accusing you of trying to poison him.",
    initial_dialogue: "I'm not taking those pills! You already gave them to me this morning. You're trying to make me sick so you can take my house!",
    initial_agitation: 6
  },
  {
    id: "shower_refusal",
    title: "Shower Agitation",
    description: "It is late afternoon and Arthur resists taking a shower. He gets defensive and says he just showered yesterday.",
    initial_dialogue: "Why are you always nagging me to wash? I took a shower yesterday! Leave me alone, I'm clean enough!",
    initial_agitation: 5
  },
  {
    id: "go_home",
    title: "Wants to 'Go Home'",
    description: "Arthur starts packing a small bag in the living room. He is crying and saying he needs to go to his mother's house.",
    initial_dialogue: "Where is my suitcase? I have to go home right now. My mother is waiting for me to help with the farm chores. Let me out!",
    initial_agitation: 7
  }
];

function App() {
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
      setSelectedFile(e.target.files[0]);
      setInputText('');
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
        tip = "Trap detected: Attempted to use logic/authority ('have to', 'doctor') which triggers paranoia. Try validating Arthur's mistrust.";
      } else if (inputLower.includes('sorry') || inputLower.includes('tea') || inputLower.includes('cookies') || inputLower.includes('carpentry') || inputLower.includes('band')) {
        responseText = "Well... I do like chamomile tea. But make sure you don't touch my papers in the living room. Where are my carpentry magazines?";
        deltaAgitation = -2;
        tip = "Success: You validated his distraction or offered a preferred comfort (tea/carpentry). Agitation decreases.";
      } else {
        responseText = "Leave me alone! Why are you standing there holding that bottle? It looks toxic!";
        deltaAgitation = 0;
        tip = "Tip: Put the pills away. Focus on validation therapy (agree with his feelings) or redirection.";
      }
    } else if (selectedScenario.id === 'shower_refusal') {
      if (inputLower.includes('dirty') || inputLower.includes('smell') || inputLower.includes('showered') || inputLower.includes('yesterday')) {
        responseText = "I do NOT smell! You are insulting me in my own house. I'm not going in that bathroom, it's freezing!";
        deltaAgitation = 2;
        tip = "Trap detected: Correcting his memory ('yesterday') or accusing him of smelling triggers shame. Validate that he feels clean, or check room comfort.";
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
        tip = "Critical Trap: Reality orientation (telling him his mother is dead or house is sold) triggers traumatic grief. Validate his memory instead.";
      } else if (inputLower.includes('tell me') || inputLower.includes('mother') || inputLower.includes('farm') || inputLower.includes('childhood')) {
        responseText = "My mother... she always made the best apple pies on Sundays. The farm had three horses... one was named Barnaby.";
        deltaAgitation = -2;
        tip = "Success: Validation therapy. By asking him to share a memory about his mother/farm, you validated his emotions and can now redirect him.";
      } else {
        responseText = "Get out of my way, I need to walk to the bus stop. The bus comes at 5:00!";
        deltaAgitation = 1;
        tip = "Tip: Ask about his home or childhood. Try: 'You really want to help your mom. Tell me about the chores you did.'"
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
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div className="api-status">
            <span className={`status-dot ${backendStatus === 'online' ? 'online' : backendStatus === 'offline' ? 'offline' : ''}`}></span>
            <span>Agent Server: {backendStatus.toUpperCase()}</span>
          </div>
          
          {backendStatus === 'online' && (
            <button 
              className="btn btn-secondary" 
              style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
              onClick={seedDatabase}
              disabled={isSeeding}
            >
              <Database size={14} />
              {isSeeding ? 'Seeding...' : 'Seed RAG DB'}
            </button>
          )}
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
          <span>Guidelines RAG</span>
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
                <label className="form-label">Option A: Upload Video/Audio Interaction</label>
                <div 
                  className="upload-dropzone"
                  onClick={() => document.getElementById('file-upload').click()}
                >
                  <Upload size={32} style={{ color: 'var(--primary)' }} />
                  <p style={{ fontSize: '0.9rem', fontWeight: 600 }}>Drag file here or click to browse</p>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Supports MP4, MOV, MP3, WAV</p>
                </div>
                <input 
                  type="file" 
                  id="file-upload" 
                  style={{ display: 'none' }} 
                  onChange={handleFileChange}
                  accept="video/*,audio/*"
                />
                {selectedFile && (
                  <div className="file-preview">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Activity size={16} style={{ color: 'var(--primary)' }} />
                      <span style={{ fontWeight: 500 }}>{selectedFile.name}</span>
                    </div>
                    <button 
                      className="tag-delete-btn"
                      onClick={() => setSelectedFile(null)}
                    >
                      <Trash2 size={16} />
                    </button>
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
                  placeholder="Example: Dad got agitated when I showed him his heart pill. He accused me of stealing and yelled that he wouldn't take it. I showed him the medicine bottle and told him he was wrong, which made him shout louder..."
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
                    <span>Processing Team...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={16} />
                    <span>Run 5-Agent Analysis</span>
                  </>
                )}
              </button>

              {/* 5-Agent Processing Flow Visualizer */}
              {isAnalyzing && (
                <div className="pipeline-status">
                  <p style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary)' }}>Orchestrating Specialized Agents:</p>
                  
                  <div className={`pipeline-step ${analysisStep === 1 ? 'active' : analysisStep > 1 ? 'completed' : ''}`}>
                    {analysisStep === 1 ? <div className="spinner" /> : <CheckCircle2 size={14} />}
                    <span>Agent 1: Interaction Analysis (Verbal & Non-verbal Cues)</span>
                  </div>
                  
                  <div className={`pipeline-step ${analysisStep === 2 ? 'active' : analysisStep > 2 ? 'completed' : ''}`}>
                    {analysisStep === 2 ? <div className="spinner" /> : <CheckCircle2 size={14} />}
                    <span>Agent 2: Patient Context Integration (Med Schedule, Triggers)</span>
                  </div>
                  
                  <div className={`pipeline-step ${analysisStep === 3 ? 'active' : analysisStep > 3 ? 'completed' : ''}`}>
                    {analysisStep === 3 ? <div className="spinner" /> : <CheckCircle2 size={14} />}
                    <span>Agent 3: Clinical Care RAG Ingestion (Nursing/OT Protocols)</span>
                  </div>
                  
                  <div className={`pipeline-step ${analysisStep === 4 ? 'active' : analysisStep > 4 ? 'completed' : ''}`}>
                    {analysisStep === 4 ? <div className="spinner" /> : <CheckCircle2 size={14} />}
                    <span>Agent 4: Safety & Medical Escalation Risk Check</span>
                  </div>
                  
                  <div className={`pipeline-step ${analysisStep === 5 ? 'active' : ''}`}>
                    {analysisStep === 5 ? <div className="spinner" /> : <CheckCircle2 size={14} />}
                    <span>Agent 5: Caregiver Coaching Synthesis (Empathetic Dialogue Scripts)</span>
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
                  <p style={{ fontWeight: 600, color: 'var(--text-main)' }}>Consulting Specialized Agent Panel...</p>
                  <p style={{ fontSize: '0.85rem', marginTop: '0.25rem' }}>Analyzing verbal tone, clinical context, care guidelines, and safety hazards.</p>
                </div>
              )}

              {analysisResult && !isAnalyzing && (
                <div className="feedback-grid fade-in">
                  
                  {/* Summary & Behavior Recognition */}
                  <div className="glass-card feedback-full-width" style={{ background: 'rgba(15, 23, 42, 0.3)', gap: '0.75rem' }}>
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
                      Clinical Care Protocols (Synthesized via RAG)
                    </h3>
                    
                    {analysisResult.recommendations.map((rec, idx) => (
                      <div key={idx} className="glass-card" style={{ background: 'rgba(99, 102, 241, 0.05)', border: '1px solid rgba(99, 102, 241, 0.15)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontWeight: 700, color: 'var(--secondary)' }}>{rec.strategy_name}</span>
                          <span className="api-status" style={{ fontSize: '0.75rem', padding: '0.15rem 0.5rem' }}>Grounded Advice</span>
                        </div>
                        <p style={{ fontSize: '0.9rem', color: 'var(--text-light)' }}>{rec.description}</p>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', borderTop: '1px dashed rgba(255, 255, 255, 0.05)', paddingTop: '0.5rem' }}>
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
                    <div key={idx} className="tag-pill" style={{ borderColor: 'rgba(99, 102, 241, 0.2)', color: '#c7d2fe' }}>
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
                Select a scenario. The simulated patient agent (Arthur) will respond realistically. Practice validation therapy and redirection to keep his agitation low.
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
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Training Chat with Arthur</h3>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Scenario: {selectedScenario.title}</p>
                </div>
                
                {/* Agitation Score Meter */}
                <div className="agitation-meter-wrapper">
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>Arthur's Agitation:</span>
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
                    Arthur is thinking...
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
                  placeholder="Type your response to Arthur..."
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
              Guidelines Knowledge Base (RAG)
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Search the local vector database of dementia care guidelines. The AI Agent uses this database to retrieve verified caregiver protocols.
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
                {ragResults.length > 0 ? 'Search Results' : 'Default Guidelines Injected in ChromaDB'}
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
                        <span className="api-status" style={{ fontSize: '0.75rem', padding: '0.15rem 0.5rem', background: 'var(--secondary-glow)', color: '#a5b4fc', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
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
