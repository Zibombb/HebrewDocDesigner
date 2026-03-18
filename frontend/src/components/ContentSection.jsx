import { useState, useEffect, useRef } from 'react'
import { FileText, Upload, Trash2, Loader, Tag, Database, X } from 'lucide-react'
import { uploadContent, listSources, deleteSource, listTopics } from '../api/client'

export default function ContentSection({ showToast }) {
  const [sources, setSources] = useState([])
  const [topics, setTopics] = useState([])
  const [totalChunks, setTotalChunks] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(null)
  const fileRef = useRef()

  const load = async () => {
    const [srcs, topicData] = await Promise.all([
      listSources().catch(() => []),
      listTopics().catch(() => ({ topics: [], total_chunks: 0 })),
    ])
    setSources(srcs)
    setTopics(topicData.topics || [])
    setTotalChunks(topicData.total_chunks || 0)
  }

  useEffect(() => { load() }, [])

  const handleUpload = async (files) => {
    const fileList = Array.from(files)
    if (!fileList.length) return

    setUploading(true)
    let success = 0
    for (const file of fileList) {
      setUploadProgress(`מעלה: ${file.name}...`)
      try {
        await uploadContent(file)
        success++
      } catch (e) {
        showToast(`שגיאה ב-${file.name}: ${e.message}`, 'error')
      }
    }
    setUploading(false)
    setUploadProgress(null)
    if (success > 0) {
      showToast(`${success} קבצים נוספו בהצלחה`)
      await load()
    }
  }

  const handleDelete = async (id, name) => {
    if (!confirm(`למחוק את "${name}"?`)) return
    await deleteSource(id).catch(e => showToast(e.message, 'error'))
    showToast('המקור נמחק')
    await load()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    handleUpload(e.dataTransfer.files)
  }

  const extIcon = (name) => {
    const ext = name.split('.').pop().toLowerCase()
    const icons = { pdf: '📄', docx: '📝', doc: '📝', txt: '📃', md: '📃' }
    return icons[ext] || '📎'
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Upload + Sources */}
      <div className="lg:col-span-2 space-y-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-blue-600/20 rounded-xl flex items-center justify-center">
            <Upload size={20} className="text-blue-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">חומרי גלם</h2>
            <p className="text-xs text-slate-400">העלה קבצים שישמשו כבסיס לספר</p>
          </div>
        </div>

        {/* Drop Zone */}
        <div
          onDrop={handleDrop}
          onDragOver={e => e.preventDefault()}
          onClick={() => !uploading && fileRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all
            ${uploading
              ? 'border-blue-500 bg-blue-500/5'
              : 'border-slate-700 hover:border-blue-500 hover:bg-blue-500/5'
            }`}
        >
          <input
            ref={fileRef}
            type="file"
            multiple
            accept=".pdf,.docx,.doc,.txt,.md"
            className="hidden"
            onChange={e => handleUpload(e.target.files)}
          />
          {uploading ? (
            <div className="flex flex-col items-center gap-3">
              <Loader className="animate-spin text-blue-400" size={32} />
              <p className="text-sm text-blue-300">{uploadProgress}</p>
              <p className="text-xs text-slate-500">מנתח ומאנדקס את הקובץ...</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3">
              <Upload size={32} className="text-slate-600" />
              <div>
                <p className="text-sm text-slate-300">גרור קבצים לכאן או לחץ לבחירה</p>
                <p className="text-xs text-slate-500 mt-1">PDF, DOCX, TXT, MD — עד 100MB לקובץ</p>
              </div>
            </div>
          )}
        </div>

        {/* Sources List */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-300 flex items-center gap-2">
            <Database size={14} />
            מקורות שנטענו ({sources.length})
          </h3>
          {sources.length === 0 ? (
            <div className="text-center py-8 text-slate-600 text-sm">
              טרם הועלו קבצים
            </div>
          ) : (
            sources.map(source => (
              <div
                key={source.id}
                className="flex items-start justify-between bg-slate-800 rounded-xl p-4 fade-in"
              >
                <div className="flex items-start gap-3 flex-1 min-w-0">
                  <span className="text-2xl mt-0.5">{extIcon(source.name)}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">{source.name}</p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {source.chunk_count} קטעים · {new Date(source.added_at).toLocaleDateString('he-IL')}
                    </p>
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {source.topics.slice(0, 4).map(t => (
                        <span key={t} className="text-xs px-2 py-0.5 bg-slate-700 text-slate-400 rounded-full">
                          {t}
                        </span>
                      ))}
                      {source.topics.length > 4 && (
                        <span className="text-xs text-slate-600">+{source.topics.length - 4}</span>
                      )}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(source.id, source.name)}
                  className="text-slate-600 hover:text-red-400 transition-colors mr-2 mt-0.5"
                >
                  <Trash2 size={15} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Topics sidebar */}
      <div>
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 bg-violet-600/20 rounded-xl flex items-center justify-center">
            <Tag size={20} className="text-violet-400" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-white">נושאים באינדקס</h2>
            <p className="text-xs text-slate-400">{totalChunks} קטעי תוכן</p>
          </div>
        </div>

        <div className="bg-slate-800 rounded-2xl p-4 space-y-2 max-h-[500px] overflow-y-auto">
          {topics.length === 0 ? (
            <p className="text-slate-600 text-xs text-center py-4">
              העלה חומרים כדי לראות נושאים
            </p>
          ) : (
            topics.map(topic => (
              <div key={topic} className="flex items-center gap-2 text-xs text-slate-400 py-1.5
                border-b border-slate-700/50 last:border-0">
                <span className="w-1.5 h-1.5 bg-violet-500 rounded-full flex-shrink-0" />
                {topic}
              </div>
            ))
          )}
        </div>

        <div className="mt-4 bg-slate-800/50 border border-slate-700 rounded-xl p-4">
          <h3 className="text-xs font-medium text-slate-400 mb-2">מה קורה בעיבוד?</h3>
          <ul className="text-xs text-slate-500 space-y-1.5">
            <li className="flex items-start gap-2">
              <span className="text-blue-400 mt-0.5">1.</span>
              חילוץ טקסט מהקובץ
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-400 mt-0.5">2.</span>
              פיצול לקטעים לוגיים
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-400 mt-0.5">3.</span>
              ניתוח כל קטע: נושא, מושגים, סוג
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-400 mt-0.5">4.</span>
              אינדוקס וקטורי לחיפוש סמנטי
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}
