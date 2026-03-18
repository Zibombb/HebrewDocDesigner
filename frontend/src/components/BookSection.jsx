import { useState, useEffect, useRef } from 'react'
import { BookOpen, Plus, Loader, Play, CheckCircle, Edit3, Save, X, ChevronDown, ChevronUp, Trash2, List } from 'lucide-react'
import { createBook, listBooks, getBook, deleteBook, updateChapterContent, streamChapter } from '../api/client'

function ChapterCard({ chapter, bookId, onUpdate, showToast }) {
  const [expanded, setExpanded] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [editing, setEditing] = useState(false)
  const [editContent, setEditContent] = useState(chapter.content || '')
  const [streamedText, setStreamedText] = useState('')
  const streamRef = useRef('')

  const handleGenerate = () => {
    setGenerating(true)
    setExpanded(true)
    streamRef.current = ''
    setStreamedText('')

    streamChapter(
      bookId,
      chapter.id,
      (text) => {
        streamRef.current += text
        setStreamedText(streamRef.current)
      },
      () => {
        setGenerating(false)
        onUpdate()
      },
      (err) => {
        setGenerating(false)
        showToast(typeof err === 'string' ? err : 'שגיאה ביצירת הפרק', 'error')
      }
    )
  }

  const handleSave = async () => {
    try {
      await updateChapterContent(bookId, chapter.id, editContent)
      setEditing(false)
      onUpdate()
      showToast('הפרק נשמר')
    } catch (e) {
      showToast(e.message, 'error')
    }
  }

  const displayContent = generating ? streamedText : (chapter.content || '')
  const statusColor = {
    pending: 'text-slate-500',
    generating: 'text-amber-400',
    done: 'text-emerald-400',
  }[chapter.status] || 'text-slate-500'

  const statusLabel = {
    pending: 'ממתין',
    generating: 'מייצר...',
    done: 'הושלם',
  }[chapter.status] || ''

  return (
    <div className="bg-slate-800 rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 cursor-pointer"
        onClick={() => !generating && setExpanded(!expanded)}>
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <div className={`w-7 h-7 rounded-full border-2 flex items-center justify-center text-xs flex-shrink-0
            ${chapter.status === 'done' ? 'border-emerald-500 bg-emerald-500/20' :
              chapter.status === 'generating' ? 'border-amber-500 bg-amber-500/20' :
              'border-slate-600 bg-slate-700'}`}>
            {chapter.status === 'done' ? <CheckCircle size={14} className="text-emerald-400" /> :
             chapter.status === 'generating' ? <Loader size={14} className="text-amber-400 animate-spin" /> :
             <span className="text-slate-400">{chapter.order + 1}</span>}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-white truncate">{chapter.title}</p>
            <p className="text-xs text-slate-500 truncate">{chapter.description}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 mr-2">
          <span className={`text-xs ${statusColor}`}>{statusLabel}</span>
          {chapter.status === 'pending' && !generating && (
            <button
              onClick={e => { e.stopPropagation(); handleGenerate() }}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500
                rounded-lg text-xs font-medium text-white transition-colors"
            >
              <Play size={12} />
              צור
            </button>
          )}
          {chapter.status === 'done' && !generating && (
            <button
              onClick={e => { e.stopPropagation(); handleGenerate() }}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-700 hover:bg-slate-600
                rounded-lg text-xs text-slate-400 transition-colors"
            >
              <Play size={12} />
              יצור מחדש
            </button>
          )}
          {!generating && (
            expanded ? <ChevronUp size={16} className="text-slate-500" /> :
            <ChevronDown size={16} className="text-slate-500" />
          )}
        </div>
      </div>

      {/* Content */}
      {expanded && (
        <div className="border-t border-slate-700 p-4">
          {generating && streamedText ? (
            <div className="prose-rtl text-sm text-slate-300 whitespace-pre-wrap leading-relaxed cursor-blink">
              {streamedText}
            </div>
          ) : editing ? (
            <div className="space-y-3">
              <textarea
                value={editContent}
                onChange={e => setEditContent(e.target.value)}
                rows={15}
                className="w-full bg-slate-900 border border-slate-600 rounded-xl p-4 text-sm
                  text-slate-200 focus:outline-none focus:border-indigo-500 resize-none"
                dir="rtl"
              />
              <div className="flex gap-2">
                <button onClick={handleSave}
                  className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500
                    rounded-lg text-xs font-medium text-white transition-colors">
                  <Save size={12} /> שמור
                </button>
                <button onClick={() => setEditing(false)}
                  className="flex items-center gap-1.5 px-4 py-2 bg-slate-700 hover:bg-slate-600
                    rounded-lg text-xs text-slate-300 transition-colors">
                  <X size={12} /> ביטול
                </button>
              </div>
            </div>
          ) : displayContent ? (
            <div className="space-y-3">
              <div className="prose-rtl text-sm text-slate-300 whitespace-pre-wrap leading-relaxed max-h-80 overflow-y-auto">
                {displayContent}
              </div>
              <button
                onClick={() => { setEditContent(displayContent); setEditing(true) }}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-700 hover:bg-slate-600
                  rounded-lg text-xs text-slate-300 transition-colors"
              >
                <Edit3 size={12} /> ערוך
              </button>
            </div>
          ) : (
            <p className="text-slate-600 text-xs text-center py-4">
              לחץ "צור" כדי לייצר את תוכן הפרק
            </p>
          )}
        </div>
      )}
    </div>
  )
}


function BookView({ book, onBack, showToast }) {
  const [currentBook, setCurrentBook] = useState(book)

  const refresh = async () => {
    const updated = await getBook(book.id).catch(() => null)
    if (updated) setCurrentBook(updated)
  }

  const handleGenerateAll = async () => {
    const pending = currentBook.chapters.filter(c => c.status === 'pending')
    if (!pending.length) {
      showToast('כל הפרקים כבר נוצרו')
      return
    }
    // Generate sequentially
    for (const chapter of pending) {
      await new Promise((resolve, reject) => {
        streamChapter(currentBook.id, chapter.id, () => {}, () => resolve(), reject)
      }).catch(e => showToast(`שגיאה בפרק "${chapter.title}": ${e}`, 'error'))
      await refresh()
    }
  }

  const doneCount = currentBook.chapters.filter(c => c.status === 'done').length

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <button onClick={onBack} className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm">
          ← חזרה לרשימת הספרים
        </button>
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-500">{doneCount}/{currentBook.chapters.length} פרקים הושלמו</span>
          <button
            onClick={handleGenerateAll}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500
              rounded-lg text-sm font-medium text-white transition-colors"
          >
            <Play size={14} />
            צור הכל
          </button>
        </div>
      </div>

      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white">{currentBook.title}</h2>
        <p className="text-slate-400 text-sm mt-1">{currentBook.description}</p>
      </div>

      <div className="space-y-3">
        {currentBook.chapters.map(chapter => (
          <ChapterCard
            key={chapter.id}
            chapter={chapter}
            bookId={currentBook.id}
            onUpdate={refresh}
            showToast={showToast}
          />
        ))}
      </div>
    </div>
  )
}


export default function BookSection({ showToast }) {
  const [books, setBooks] = useState([])
  const [selectedBook, setSelectedBook] = useState(null)
  const [creating, setCreating] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    title: '',
    description: '',
    chapter_ideas: '',
    n_chapters: 5,
  })

  const loadBooks = async () => {
    const list = await listBooks().catch(() => [])
    setBooks(list)
  }

  useEffect(() => { loadBooks() }, [])

  const handleCreate = async () => {
    if (!form.title.trim()) {
      showToast('יש להזין כותרת לספר', 'error')
      return
    }
    setCreating(true)
    try {
      const book = await createBook(form)
      await loadBooks()
      setSelectedBook(book)
      setShowForm(false)
      setForm({ title: '', description: '', chapter_ideas: '', n_chapters: 5 })
      showToast('מבנה הספר נוצר!')
    } catch (e) {
      showToast(e.message, 'error')
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (id, title, e) => {
    e.stopPropagation()
    if (!confirm(`למחוק את "${title}"?`)) return
    await deleteBook(id).catch(e => showToast(e.message, 'error'))
    await loadBooks()
    showToast('הספר נמחק')
  }

  if (selectedBook) {
    return (
      <BookView
        book={selectedBook}
        onBack={async () => { setSelectedBook(null); await loadBooks() }}
        showToast={showToast}
      />
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-amber-600/20 rounded-xl flex items-center justify-center">
            <BookOpen size={20} className="text-amber-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">הספרים שלי</h2>
            <p className="text-xs text-slate-400">צור וצור ספרים בקולך האישי</p>
          </div>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-500
            rounded-lg text-sm font-medium text-white transition-colors"
        >
          <Plus size={16} />
          ספר חדש
        </button>
      </div>

      {/* Create Form */}
      {showForm && (
        <div className="bg-slate-800 rounded-2xl p-6 mb-6 fade-in">
          <h3 className="text-base font-semibold text-white mb-4">יצירת ספר חדש</h3>
          <div className="space-y-4">
            <div>
              <label className="text-xs text-slate-400 block mb-1.5">כותרת הספר *</label>
              <input
                value={form.title}
                onChange={e => setForm({...form, title: e.target.value})}
                placeholder="למשל: מנהיגות בעידן ה-AI"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm
                  text-white placeholder-slate-600 focus:outline-none focus:border-amber-500"
                dir="rtl"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1.5">תיאור הספר</label>
              <textarea
                value={form.description}
                onChange={e => setForm({...form, description: e.target.value})}
                placeholder="על מה הספר? מי הקהל? מה המסר המרכזי?"
                rows={3}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm
                  text-white placeholder-slate-600 focus:outline-none focus:border-amber-500 resize-none"
                dir="rtl"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1.5">רעיונות לפרקים (אופציונלי)</label>
              <textarea
                value={form.chapter_ideas}
                onChange={e => setForm({...form, chapter_ideas: e.target.value})}
                placeholder="פרק על X, פרק על Y, פרק על Z..."
                rows={2}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm
                  text-white placeholder-slate-600 focus:outline-none focus:border-amber-500 resize-none"
                dir="rtl"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1.5">מספר פרקים: {form.n_chapters}</label>
              <input
                type="range" min={3} max={15} value={form.n_chapters}
                onChange={e => setForm({...form, n_chapters: parseInt(e.target.value)})}
                className="w-full accent-amber-500"
              />
              <div className="flex justify-between text-xs text-slate-600 mt-1">
                <span>3</span><span>15</span>
              </div>
            </div>
            <div className="flex gap-3 pt-2">
              <button
                onClick={handleCreate}
                disabled={creating}
                className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-amber-600 hover:bg-amber-500
                  disabled:opacity-50 rounded-xl text-sm font-medium text-white transition-colors"
              >
                {creating ? <><Loader size={16} className="animate-spin" /> יוצר מבנה...</> :
                 <><BookOpen size={16} /> צור ספר</>}
              </button>
              <button
                onClick={() => setShowForm(false)}
                className="px-4 py-2.5 bg-slate-700 hover:bg-slate-600 rounded-xl text-sm text-slate-300 transition-colors"
              >
                ביטול
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Books Grid */}
      {books.length === 0 ? (
        <div className="text-center py-16">
          <BookOpen size={48} className="text-slate-700 mx-auto mb-4" />
          <p className="text-slate-500">אין ספרים עדיין</p>
          <p className="text-slate-600 text-sm mt-1">לחץ "ספר חדש" כדי להתחיל</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {books.map(book => {
            const done = book.chapters.filter(c => c.status === 'done').length
            const total = book.chapters.length
            const pct = total > 0 ? Math.round(done / total * 100) : 0
            return (
              <div
                key={book.id}
                onClick={() => setSelectedBook(book)}
                className="bg-slate-800 hover:bg-slate-750 border border-slate-700 hover:border-amber-500/50
                  rounded-2xl p-5 cursor-pointer transition-all group"
              >
                <div className="flex items-start justify-between mb-3">
                  <BookOpen size={20} className="text-amber-400 flex-shrink-0" />
                  <button
                    onClick={e => handleDelete(book.id, book.title, e)}
                    className="text-slate-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
                <h3 className="text-sm font-semibold text-white mb-1 line-clamp-2">{book.title}</h3>
                {book.description && (
                  <p className="text-xs text-slate-500 line-clamp-2 mb-3">{book.description}</p>
                )}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-500">{total} פרקים</span>
                    <span className={pct === 100 ? 'text-emerald-400' : 'text-slate-500'}>{done}/{total} הושלמו</span>
                  </div>
                  <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-amber-500 rounded-full transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
                <p className="text-xs text-slate-600 mt-3">
                  {new Date(book.created_at).toLocaleDateString('he-IL')}
                </p>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
