import { Mic, FileText, BookOpen } from 'lucide-react'

const tabs = [
  { id: 'voice', label: 'קול', icon: Mic, desc: 'ניתוח סגנון כתיבה' },
  { id: 'content', label: 'חומרים', icon: FileText, desc: 'העלאת חומרי גלם' },
  { id: 'book', label: 'ספר', icon: BookOpen, desc: 'יצירת הספר' },
]

export default function Layout({ children, activeTab, onTabChange }) {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-slate-900 border-b border-slate-700 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-white">✍️ כותב ספרים AI</h1>
            <p className="text-xs text-slate-400 mt-0.5">כותב ספרים בקולך האישי</p>
          </div>
          <nav className="flex gap-1">
            {tabs.map(({ id, label, icon: Icon, desc }) => (
              <button
                key={id}
                onClick={() => onTabChange(id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all
                  ${activeTab === id
                    ? 'bg-indigo-600 text-white'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                  }`}
                title={desc}
              >
                <Icon size={16} />
                {label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-8">
        {children}
      </main>
    </div>
  )
}
