const BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'שגיאה לא ידועה')
  }
  return res.json()
}

// Voice
export const analyzeVoice = (samples) =>
  request('/voice/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ samples }),
  })

export const getVoiceProfile = () => request('/voice/profile')

export const deleteVoiceProfile = () =>
  request('/voice/profile', { method: 'DELETE' })

// Content
export const uploadContent = (file) => {
  const form = new FormData()
  form.append('file', file)
  return request('/content/upload', { method: 'POST', body: form })
}

export const listSources = () => request('/content/sources')

export const deleteSource = (id) =>
  request(`/content/sources/${id}`, { method: 'DELETE' })

export const listTopics = () => request('/content/topics')

// Books
export const createBook = (data) =>
  request('/book/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

export const listBooks = () => request('/book/list')

export const getBook = (id) => request(`/book/${id}`)

export const deleteBook = (id) =>
  request(`/book/${id}`, { method: 'DELETE' })

export const updateChapterContent = (bookId, chapterId, content) =>
  request(`/book/${bookId}/chapters/${chapterId}/content`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })

export function streamChapter(bookId, chapterId, onText, onDone, onError) {
  fetch('/api/book/generate-chapter', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ book_id: bookId, chapter_id: chapterId }),
  }).then(async (res) => {
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'שגיאה' }))
      onError(err.detail || 'שגיאה ביצירת הפרק')
      return
    }
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop()
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.text) onText(data.text)
            if (data.done) onDone()
            if (data.error) onError(data.error)
          } catch {}
        }
      }
    }
  }).catch(onError)
}
