import { useState, useEffect } from 'react'
import { Mic, Plus, Trash2, Loader, CheckCircle, TrendingUp, FileText } from 'lucide-react'
import { analyzeVoice, getVoiceProfile, deleteVoiceProfile } from '../api/client'

function ScoreBar({ label, value, color = 'indigo' }) {
  const colors = {
    indigo: 'bg-indigo-500',
    emerald: 'bg-emerald-500',
    amber: 'bg-amber-500',
  }
  return (
    <div>
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span>{label}</span>
        <span className="font-medium text-white">{value}/10</span>
      </div>
      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full ${colors[color]} rounded-full transition-all duration-700`}
          style={{ width: `${value * 10}%` }}
        />
      </div>
    </div>
  )
}

export default function VoiceSection({ showToast }) {
  const [samples, setSamples] = useState([''])
  const [loading, setLoading] = useState(false)
  const [profile, setProfile] = useState(null)
  const [loadingProfile, setLoadingProfile] = useState(true)

  useEffect(() => {
    getVoiceProfile()
      .then(setProfile)
      .catch(() => {})
      .finally(() => setLoadingProfile(false))
  }, [])

  const addSample = () => setSamples([...samples, ''])
  const removeSample = (i) => setSamples(samples.filter((_, idx) => idx !== i))
  const updateSample = (i, val) => setSamples(samples.map((s, idx) => idx === i ? val : s))

  const handleAnalyze = async () => {
    const valid = samples.filter(s => s.trim().length > 50)
    if (valid.length === 0) {
      showToast('יש להזין לפחות דוגמת כתיבה אחת (לפחות 50 תווים)', 'error')
      return
    }
    setLoading(true)
    try {
      const result = await analyzeVoice(valid)
      setProfile(result)
      showToast('ניתוח הקול הושלם בהצלחה!')
    } catch (e) {
      showToast(e.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('למחוק את הפרופיל הקולי?')) return
    await deleteVoiceProfile().catch(() => {})
    setProfile(null)
    showToast('הפרופיל נמחק')
  }

  if (loadingProfile) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader className="animate-spin text-indigo-400" size={32} />
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      {/* Input Panel */}
      <div className="space-y-4">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-indigo-600/20 rounded-xl flex items-center justify-center">
            <Mic size={20} className="text-indigo-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">דוגמאות כתיבה</h2>
            <p className="text-xs text-slate-400">הדבק טקסטים שכתבת — מאמרים, פוסטים, ספרים</p>
          </div>
        </div>

        {samples.map((sample, i) => (
          <div key={i} className="relative">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-medium text-slate-400">דוגמה {i + 1}</span>
              {samples.length > 1 && (
                <button onClick={() => removeSample(i)} className="text-slate-600 hover:text-red-400 transition-colors">
                  <Trash2 size={14} />
                </button>
              )}
            </div>
            <textarea
              value={sample}
              onChange={e => updateSample(i, e.target.value)}
              placeholder="הדבק כאן טקסט שכתבת..."
              rows={6}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl p-4 text-sm text-slate-200
                placeholder-slate-600 focus:outline-none focus:border-indigo-500 resize-none transition-colors"
              dir="rtl"
            />
            <div className="text-xs text-slate-600 mt-1 text-left">{sample.length} תווים</div>
          </div>
        ))}

        <div className="flex gap-3">
          <button
            onClick={addSample}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700
              border border-slate-700 rounded-lg text-sm text-slate-300 transition-colors"
          >
            <Plus size={16} />
            הוסף דוגמה
          </button>
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2
              bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed
              rounded-lg text-sm font-medium text-white transition-colors"
          >
            {loading ? (
              <><Loader size={16} className="animate-spin" /> מנתח...</>
            ) : (
              <><Mic size={16} /> נתח את הקול שלי</>
            )}
          </button>
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
          <h3 className="text-xs font-medium text-slate-400 mb-2 flex items-center gap-2">
            <FileText size={12} />
            טיפים לדוגמאות טובות
          </h3>
          <ul className="text-xs text-slate-500 space-y-1">
            <li>• הוסף לפחות 2-3 דוגמאות מסוגים שונים</li>
            <li>• דוגמאות ארוכות יותר = ניתוח מדויק יותר</li>
            <li>• כלול מאמרים, פוסטים, מיילים — מה שמייצג אותך</li>
            <li>• אורך מינימלי: 50 תווים לדוגמה</li>
          </ul>
        </div>
      </div>

      {/* Profile Panel */}
      <div>
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-emerald-600/20 rounded-xl flex items-center justify-center">
            <TrendingUp size={20} className="text-emerald-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">פרופיל קולי</h2>
            <p className="text-xs text-slate-400">תוצאות ניתוח הסגנון שלך</p>
          </div>
        </div>

        {!profile ? (
          <div className="bg-slate-800/30 border border-dashed border-slate-700 rounded-2xl p-10 text-center">
            <Mic size={40} className="text-slate-600 mx-auto mb-3" />
            <p className="text-slate-500 text-sm">טרם נוצר פרופיל קולי</p>
            <p className="text-slate-600 text-xs mt-1">הוסף דוגמאות כתיבה ולחץ "נתח"</p>
          </div>
        ) : (
          <div className="space-y-5 fade-in">
            {/* Scores */}
            <div className="bg-slate-800 rounded-2xl p-5 space-y-4">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <CheckCircle size={16} className="text-emerald-400" />
                מדדי סגנון
                <span className="text-xs text-slate-500 font-normal">({profile.sample_count} דוגמאות)</span>
              </h3>
              <ScoreBar label="רמת רשמיות" value={profile.formality_level} color="indigo" />
              <ScoreBar label="מורכבות משפטים" value={profile.sentence_complexity} color="emerald" />
              <ScoreBar label="עושר אוצר מילים" value={profile.vocabulary_richness} color="amber" />
            </div>

            {/* Tone Keywords */}
            <div className="bg-slate-800 rounded-2xl p-5">
              <h3 className="text-sm font-semibold text-white mb-3">מילות מפתח לטון</h3>
              <div className="flex flex-wrap gap-2">
                {profile.tone_keywords.map(kw => (
                  <span key={kw} className="px-3 py-1 bg-indigo-600/20 text-indigo-300 rounded-full text-xs border border-indigo-600/30">
                    {kw}
                  </span>
                ))}
              </div>
            </div>

            {/* Unique Phrases */}
            {profile.unique_phrases.length > 0 && (
              <div className="bg-slate-800 rounded-2xl p-5">
                <h3 className="text-sm font-semibold text-white mb-3">ביטויים ייחודיים</h3>
                <ul className="space-y-1.5">
                  {profile.unique_phrases.map(p => (
                    <li key={p} className="text-xs text-slate-400 flex items-start gap-2">
                      <span className="text-indigo-500 mt-0.5">•</span>{p}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Style Description */}
            <div className="bg-slate-800 rounded-2xl p-5">
              <h3 className="text-sm font-semibold text-white mb-3">תיאור הסגנון</h3>
              <p className="text-xs text-slate-400 leading-relaxed" dir="rtl">
                {profile.style_description}
              </p>
            </div>

            <button
              onClick={handleDelete}
              className="w-full py-2 bg-slate-800 hover:bg-red-900/30 border border-slate-700
                hover:border-red-700 text-slate-500 hover:text-red-400 rounded-xl text-xs transition-all"
            >
              מחק פרופיל ויצור מחדש
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
