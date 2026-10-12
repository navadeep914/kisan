import React, { useEffect, useRef, useState } from 'react'
import axios from 'axios'
import { useApp } from '../context/AppContext'
import './FarmerAdvisory.css'

const copy = {
  en: {
    title: 'Farmer Advisory Assistant',
    subtitle: 'Ask a crop question in English, हिंदी, or తెలుగు.',
    question: 'Your question',
    placeholder: 'For example: Rice leaves are turning yellow. What should I check?',
    send: 'Get advice',
    listening: 'Listening… speak now',
    mic: 'Speak',
    stop: 'Stop',
    language: 'Voice language',
    profile: 'Your farm profile',
    location: 'Village / district',
    crops: 'Crops grown',
    soil: 'Soil type',
    land: 'Land size',
    save: 'Save profile',
    saved: 'Profile saved',
    history: 'Recent interactions',
    sources: 'Knowledge sources',
    intent: 'Intent',
    crop: 'Crop',
    stage: 'Growth stage',
    symptoms: 'Symptoms',
    season: 'Season',
    speakAnswer: 'Read aloud',
    noHistory: 'Your questions and advice will appear here.',
    noSources: 'No matching knowledge was found.',
    loading: 'Preparing grounded advice…',
    unsupported: 'Speech recognition is not available in this browser. Try Chrome or type your question.',
    speechError: 'Voice input could not start. Check microphone permission and try again.',
    type: 'Type',
    text: 'Text',
    voice: 'Voice',
    prompt: 'Try asking',
    savedError: 'Could not save your profile.',
    error: 'Could not get advice. Check that the backend is running and try again.',
  },
  hi: {
    title: 'कृषक सलाहकार',
    subtitle: 'फसल के बारे में हिंदी, తెలుగు या English में पूछें।',
    question: 'आपका सवाल',
    placeholder: 'उदाहरण: धान की पत्तियां पीली हो रही हैं। क्या जांचूं?',
    send: 'सलाह पाएं',
    listening: 'सुन रहा है… बोलें',
    mic: 'बोलें',
    stop: 'रोकें',
    language: 'आवाज की भाषा',
    profile: 'आपकी खेती की जानकारी',
    location: 'गांव / जिला',
    crops: 'उगाई जाने वाली फसलें',
    soil: 'मिट्टी का प्रकार',
    land: 'जमीन का आकार',
    save: 'प्रोफ़ाइल सहेजें',
    saved: 'प्रोफ़ाइल सहेजी गई',
    history: 'हाल की बातचीत',
    sources: 'ज्ञान के स्रोत',
    intent: 'सवाल का प्रकार',
    crop: 'फसल',
    stage: 'विकास चरण',
    symptoms: 'लक्षण',
    season: 'मौसम',
    speakAnswer: 'जवाब सुनें',
    noHistory: 'आपके सवाल और सलाह यहां दिखेंगे।',
    noSources: 'मिलती-जुलती जानकारी नहीं मिली।',
    loading: 'विश्वसनीय सलाह तैयार हो रही है…',
    unsupported: 'इस ब्राउज़र में आवाज पहचान उपलब्ध नहीं है। Chrome आजमाएं या सवाल लिखें।',
    speechError: 'आवाज इनपुट शुरू नहीं हुआ। माइक्रोफोन अनुमति जांचकर फिर कोशिश करें।',
    type: 'इनपुट',
    text: 'लिखित',
    voice: 'आवाज',
    prompt: 'यह पूछें',
    savedError: 'प्रोफ़ाइल सहेजी नहीं जा सकी।',
    error: 'सलाह नहीं मिल सकी। बैकएंड चल रहा है या नहीं जांचें।',
  },
  te: {
    title: 'రైతు సలహా సహాయకుడు',
    subtitle: 'పంట ప్రశ్నను తెలుగు, हिंदी లేదా Englishలో అడగండి.',
    question: 'మీ ప్రశ్న',
    placeholder: 'ఉదాహరణ: వరి ఆకులు పసుపు రంగులోకి మారుతున్నాయి. ఏమి చూడాలి?',
    send: 'సలహా పొందండి',
    listening: 'వింటున్నాను… మాట్లాడండి',
    mic: 'మాట్లాడండి',
    stop: 'ఆపండి',
    language: 'వాయిస్ భాష',
    profile: 'మీ వ్యవసాయ వివరాలు',
    location: 'గ్రామం / జిల్లా',
    crops: 'సాగు పంటలు',
    soil: 'నేల రకం',
    land: 'భూమి విస్తీర్ణం',
    save: 'ప్రొఫైల్ భద్రపరచండి',
    saved: 'ప్రొఫైల్ భద్రపరచబడింది',
    history: 'ఇటీవలి సంభాషణలు',
    sources: 'జ్ఞాన వనరులు',
    intent: 'ప్రశ్న రకం',
    crop: 'పంట',
    stage: 'పెరుగుదల దశ',
    symptoms: 'లక్షణాలు',
    season: 'సీజన్',
    speakAnswer: 'సమాధానం వినండి',
    noHistory: 'మీ ప్రశ్నలు, సలహాలు ఇక్కడ కనిపిస్తాయి.',
    noSources: 'సరిపోలే సమాచారం కనబడలేదు.',
    loading: 'ఆధారిత సలహా సిద్ధమవుతోంది…',
    unsupported: 'ఈ బ్రౌజర్‌లో వాయిస్ గుర్తింపు లేదు. Chrome ప్రయత్నించండి లేదా టైప్ చేయండి.',
    speechError: 'వాయిస్ ఇన్‌పుట్ ప్రారంభం కాలేదు. మైక్రోఫోన్ అనుమతిని తనిఖీ చేసి మళ్లీ ప్రయత్నించండి.',
    type: 'ఇన్‌పుట్',
    text: 'టెక్స్ట్',
    voice: 'వాయిస్',
    prompt: 'ఇలా అడగండి',
    savedError: 'ప్రొఫైల్ భద్రపరచలేకపోయాం.',
    error: 'సలహా పొందలేకపోయాం. బ్యాకెండ్ నడుస్తోందో తనిఖీ చేయండి.',
  },
}

const languageOptions = {
  'en-IN': { label: 'English', speech: 'en-IN' },
  'hi-IN': { label: 'हिन्दी', speech: 'hi-IN' },
  'te-IN': { label: 'తెలుగు', speech: 'te-IN' },
}

const initialProfile = { location: '', crops_grown: '', soil_type: '', land_size: '' }

function getFarmerId(accountId) {
  const storageKey = `farmer-advisory-id:${accountId || 'guest'}`
  const existing = localStorage.getItem(storageKey)
  if (existing) return existing
  const randomBytes = window.crypto?.getRandomValues?.(new Uint8Array(16))
  const id = window.crypto?.randomUUID?.()
    || (randomBytes && Array.from(randomBytes, (byte) => byte.toString(16).padStart(2, '0')).join(''))
    || `farmer-${Date.now()}-${Math.random().toString(36).slice(2)}`
  localStorage.setItem(storageKey, id)
  return id
}

export default function FarmerAdvisory({ farmerId: authenticatedFarmerId }) {
  const { language } = useApp()
  const t = copy[language] || copy.en
  const [farmerId] = useState(() => getFarmerId(authenticatedFarmerId))
  const [query, setQuery] = useState('')
  const [inputType, setInputType] = useState('text')
  const [voiceLanguage, setVoiceLanguage] = useState('en-IN')
  const [profile, setProfile] = useState(initialProfile)
  const [history, setHistory] = useState([])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [listening, setListening] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const recognitionRef = useRef(null)

  useEffect(() => {
    let mounted = true
    Promise.all([
      axios.get(`/api/advisory/profile/${encodeURIComponent(farmerId)}`),
      axios.get(`/api/advisory/history/${encodeURIComponent(farmerId)}?limit=10`),
    ]).then(([profileResponse, historyResponse]) => {
      if (!mounted) return
      const { farmer_id: _farmerId, ...savedProfile } = profileResponse.data
      setProfile({ ...initialProfile, ...savedProfile })
      setHistory(historyResponse.data.items)
    }).catch((requestError) => {
      console.error('Could not load farmer advisory data:', requestError)
      if (mounted) setError(t.error)
    })
    return () => { mounted = false }
  }, [farmerId, t.error])

  const [speaking, setSpeaking] = useState(false)
  const audioRef = useRef(null)
  const utteranceRef = useRef(null)

  useEffect(() => {
    return () => {
      recognitionRef.current?.stop()
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel()
      }
    }
  }, [])

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel()
    }
    setSpeaking(false)
  }

  const fallbackBrowserSpeech = (answer, answerLanguage) => {
    if (!window.speechSynthesis) {
      setError('Text-to-speech is not available in this browser.')
      setSpeaking(false)
      return
    }

    try {
      window.speechSynthesis.cancel()
      const cleanText = answer.replace(/[*_#`]/g, '').trim()
      const utterance = new SpeechSynthesisUtterance(cleanText)
      utteranceRef.current = utterance

      const langCode = { en: 'en-IN', hi: 'hi-IN', te: 'te-IN' }[answerLanguage] || 'en-IN'
      utterance.lang = langCode

      const voices = window.speechSynthesis.getVoices()
      const prefix = answerLanguage ? answerLanguage.slice(0, 2) : 'en'
      const matchedVoice = voices.find((v) => v.lang.toLowerCase().startsWith(prefix))
      if (matchedVoice) {
        utterance.voice = matchedVoice
      }

      utterance.onstart = () => setSpeaking(true)
      utterance.onend = () => {
        setSpeaking(false)
        utteranceRef.current = null
      }
      utterance.onerror = (e) => {
        console.error('Speech synthesis error:', e)
        setSpeaking(false)
        utteranceRef.current = null
        if (e.error !== 'interrupted' && e.error !== 'canceled') {
          setError('Text-to-speech playback error.')
        }
      }

      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume()
      }

      window.speechSynthesis.speak(utterance)
    } catch (err) {
      console.error('Browser speech error:', err)
      setSpeaking(false)
    }
  }

  const speak = async (answer, answerLanguage) => {
    if (!answer) return

    if (speaking) {
      stopAudio()
      return
    }

    stopAudio()
    setError('')
    setSpeaking(true)

    try {
      const response = await axios.post(
        '/api/advisory/tts',
        { text: answer, language: answerLanguage },
        { responseType: 'blob', timeout: 15000 }
      )
      const blob = new Blob([response.data], { type: 'audio/mpeg' })
      const audioUrl = URL.createObjectURL(blob)
      const audio = new Audio(audioUrl)
      audioRef.current = audio

      audio.onended = () => {
        setSpeaking(false)
        audioRef.current = null
        URL.revokeObjectURL(audioUrl)
      }
      audio.onerror = () => {
        setSpeaking(false)
        audioRef.current = null
        URL.revokeObjectURL(audioUrl)
        fallbackBrowserSpeech(answer, answerLanguage)
      }

      await audio.play()
    } catch (ttsErr) {
      console.warn('Backend TTS request error, falling back to browser speech:', ttsErr)
      fallbackBrowserSpeech(answer, answerLanguage)
    }
  }

  const handleVoice = () => {
    if (listening) {
      recognitionRef.current?.stop()
      return
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      setError(t.unsupported)
      return
    }
    setError('')
    const recognition = new SpeechRecognition()
    const queryBeforeVoice = query.trim()
    let finalTranscript = ''
    recognition.lang = languageOptions[voiceLanguage].speech
    recognition.interimResults = true
    recognition.continuous = false
    recognition.onresult = (event) => {
      const spokenText = Array.from(event.results)
        .filter((item) => item.isFinal)
        .map((item) => item[0].transcript.trim())
        .filter(Boolean)
        .join(' ')
      if (spokenText && spokenText !== finalTranscript) {
        finalTranscript = spokenText
        setQuery(`${queryBeforeVoice} ${spokenText}`.trim())
        setInputType('voice')
      }
    }
    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      setError(t.speechError)
      setListening(false)
    }
    recognition.onend = () => setListening(false)
    recognitionRef.current = recognition
    try {
      recognition.start()
      setListening(true)
    } catch (recognitionError) {
      console.error('Could not start speech recognition:', recognitionError)
      setError(t.speechError)
      setListening(false)
    }
  }

  const loadHistory = async () => {
    const response = await axios.get(`/api/advisory/history/${encodeURIComponent(farmerId)}?limit=10`)
    setHistory(response.data.items)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    if (!query.trim() || loading) return
    setLoading(true)
    setError('')
    setNotice('')
    setResult(null)
    try {
      const response = await axios.post('/api/advisory/query', {
        farmer_id: farmerId,
        query: query.trim(),
        input_type: inputType,
      })
      setResult(response.data)
      setQuery('')
      setInputType('text')
      await loadHistory()
    } catch (requestError) {
      console.error('Could not get farmer advisory:', requestError)
      setError(requestError.response?.data?.detail || t.error)
    } finally {
      setLoading(false)
    }
  }

  const handleProfileSave = async (event) => {
    event.preventDefault()
    setError('')
    setNotice('')
    try {
      const response = await axios.put(`/api/advisory/profile/${encodeURIComponent(farmerId)}`, profile)
      const { farmer_id: _farmerId, ...savedProfile } = response.data
      setProfile(savedProfile)
      setNotice(t.saved)
    } catch (requestError) {
      console.error('Could not save farmer profile:', requestError)
      setError(requestError.response?.data?.detail || t.savedError)
    }
  }

  const setProfileField = (field) => (event) => {
    setProfile((current) => ({ ...current, [field]: event.target.value }))
  }

  const structured = result?.parsed_query

  return (
    <section className="main farmer-advisory-page">
      <header className="fa-hero">
        <div className="fa-hero-icon" aria-hidden="true">🌾</div>
        <div>
          <p className="fa-eyebrow">BHARAT KRISHI AI</p>
          <h1>{t.title}</h1>
          <p>{t.subtitle}</p>
        </div>
      </header>

      <div className="fa-layout">
        <div className="fa-primary">
          <form className="fa-card fa-question-card" onSubmit={handleSubmit}>
            <label className="fa-card-title" htmlFor="farmer-question">{t.question}</label>
            <textarea
              id="farmer-question"
              value={query}
              onChange={(event) => {
                setQuery(event.target.value)
                setInputType('text')
              }}
              placeholder={t.placeholder}
              rows={4}
              maxLength={2000}
            />
            <div className="fa-controls">
              <label className="fa-voice-select">
                <span>{t.language}</span>
                <select value={voiceLanguage} onChange={(event) => setVoiceLanguage(event.target.value)}>
                  {Object.entries(languageOptions).map(([value, option]) => (
                    <option value={value} key={value}>{option.label}</option>
                  ))}
                </select>
              </label>
              <div className="fa-actions">
                <button className={`fa-button fa-mic ${listening ? 'is-listening' : ''}`} type="button" onClick={handleVoice}>
                  <span aria-hidden="true">{listening ? '■' : '🎙️'}</span>
                  {listening ? t.stop : t.mic}
                </button>
                <button className="fa-button fa-submit" type="submit" disabled={!query.trim() || loading}>
                  {loading ? t.loading : t.send}
                </button>
              </div>
            </div>
            {listening && <p className="fa-live-status" role="status">{t.listening}</p>}
            <p className="fa-input-kind">{t.type}: {inputType === 'voice' ? t.voice : t.text}</p>
          </form>

          {error && <p className="fa-message fa-error" role="alert">{error}</p>}
          {notice && <p className="fa-message fa-success" role="status">{notice}</p>}

          {result && (
            <article className="fa-card fa-answer-card" aria-live="polite">
              <div className="fa-answer-heading">
                <div>
                  <p className="fa-eyebrow">{t.sources}</p>
                  <h2>{t.title}</h2>
                </div>
                <button
                  className={`fa-button fa-read ${speaking ? 'is-speaking' : ''}`}
                  type="button"
                  onClick={() => speak(result.advisory, result.language)}
                  title={speaking ? (t.stop || 'Stop') : t.speakAnswer}
                >
                  {speaking ? `⏹️ ${t.stop || 'Stop'}` : `🔊 ${t.speakAnswer}`}
                </button>
              </div>
              <p className="fa-answer-text">{result.advisory}</p>
              {structured && (
                <div className="fa-parsed">
                  {[
                    [t.intent, structured.intent],
                    [t.crop, structured.crop],
                    [t.stage, structured.growth_stage],
                    [t.symptoms, structured.symptoms],
                    [t.season, structured.season],
                  ].filter(([, value]) => value).map(([label, value]) => (
                    <span className="fa-tag" key={label}><b>{label}:</b> {value}</span>
                  ))}
                </div>
              )}
              <div className="fa-source-list">
                <h3>{t.sources}</h3>
                {result.retrieved_sources.length
                  ? result.retrieved_sources.map((source) => (
                    <span className="fa-source" key={`${source.title}-${source.category}`}>
                      {source.title} <small>{Math.round(source.score * 100)}%</small>
                    </span>
                  ))
                  : <p>{t.noSources}</p>}
              </div>
            </article>
          )}
        </div>

        <aside className="fa-sidebar">
          <form className="fa-card fa-profile-card" onSubmit={handleProfileSave}>
            <h2>{t.profile}</h2>
            <label>{t.location}<input value={profile.location} onChange={setProfileField('location')} maxLength={100} /></label>
            <label>{t.crops}<input value={profile.crops_grown} onChange={setProfileField('crops_grown')} maxLength={200} /></label>
            <label>{t.soil}<input value={profile.soil_type} onChange={setProfileField('soil_type')} maxLength={80} /></label>
            <label>{t.land}<input value={profile.land_size} onChange={setProfileField('land_size')} maxLength={40} /></label>
            <button className="fa-button fa-profile-save" type="submit">{t.save}</button>
          </form>

          <section className="fa-card fa-history-card">
            <h2>{t.history}</h2>
            {history.length ? (
              <ol className="fa-history-list">
                {history.map((item) => (
                  <li key={item.id}>
                    <div className="fa-history-meta">
                      <span>{item.input_type === 'voice' ? `🎙️ ${t.voice}` : `✍️ ${t.text}`}</span>
                      <time dateTime={item.created_at}>{new Date(`${item.created_at}${item.created_at.endsWith('Z') ? '' : 'Z'}`).toLocaleString()}</time>
                      <button
                        className="fa-history-speak"
                        type="button"
                        title={t.speakAnswer}
                        onClick={() => speak(item.advisory, item.language || 'te')}
                      >
                        🔊
                      </button>
                    </div>
                    <p className="fa-history-query">{item.original_input}</p>
                    <p className="fa-history-answer">{item.advisory}</p>
                    {item.retrieved_sources.map((source) => (
                      <span className="fa-history-source" key={`${item.id}-${source.title}`}>{source.title}</span>
                    ))}
                  </li>
                ))}
              </ol>
            ) : <p className="fa-empty-history">{t.noHistory}</p>}
          </section>
        </aside>
      </div>
    </section>
  )
}
