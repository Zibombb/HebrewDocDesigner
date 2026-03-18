import { useState } from 'react'
import Layout from './components/Layout'
import VoiceSection from './components/VoiceSection'
import ContentSection from './components/ContentSection'
import BookSection from './components/BookSection'

export default function App() {
  const [activeTab, setActiveTab] = useState('voice')
  const [toast, setToast] = useState(null)

  const showToast = (message, type = 'success') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3500)
  }

  return (
    <Layout activeTab={activeTab} onTabChange={setActiveTab}>
      {toast && (
        <div className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 px-6 py-3 rounded-lg shadow-xl text-sm font-medium fade-in
          ${toast.type === 'error' ? 'bg-red-600 text-white' : 'bg-emerald-600 text-white'}`}>
          {toast.message}
        </div>
      )}
      {activeTab === 'voice' && <VoiceSection showToast={showToast} />}
      {activeTab === 'content' && <ContentSection showToast={showToast} />}
      {activeTab === 'book' && <BookSection showToast={showToast} />}
    </Layout>
  )
}
