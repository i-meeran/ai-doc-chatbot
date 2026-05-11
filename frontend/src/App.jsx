import { useState, useEffect } from 'react'
import { Brain, Github, Activity } from 'lucide-react'
import FilePanel from './components/FilePanel'
import ChatPanel from './components/ChatPanel'
import { listFiles, healthCheck } from './api'

export default function App() {
  const [files, setFiles] = useState([])
  const [health, setHealth] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const fetchFiles = async () => {
    try {
      const data = await listFiles()
      setFiles(data.files || [])
    } catch (err) {
      console.error('Could not fetch files', err)
    }
  }

  const fetchHealth = async () => {
    try {
      const data = await healthCheck()
      setHealth(data)
    } catch {
      setHealth(null)
    }
  }

  useEffect(() => {
    fetchFiles()
    fetchHealth()
  }, [])

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* Top Nav */}
      <header className="glass border-b border-ink-800/50 px-6 py-3 flex items-center justify-between shrink-0 z-10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-accent/10 border border-accent/20 flex items-center justify-center">
            <Brain size={16} className="text-accent" />
          </div>
          <div>
            <h1 className="font-display font-bold text-ink-100 text-base leading-none">DocMind</h1>
            <p className="text-ink-600 text-[10px] font-mono mt-0.5">Universal Document AI</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Health indicator */}
          {health && (
            <div className="flex items-center gap-2 text-xs font-mono text-ink-500">
              <Activity size={11} className="text-emerald-500" />
              <span>{health.total_files} files · {health.faiss_index_size} vectors</span>
            </div>
          )}

          {/* Sidebar toggle */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="btn-ghost text-xs font-mono"
          >
            {sidebarOpen ? 'Hide panel' : 'Show panel'}
          </button>
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className={`
          shrink-0 border-r border-ink-800/50 glass overflow-hidden
          transition-all duration-300 ease-in-out
          ${sidebarOpen ? 'w-72 px-4 py-4' : 'w-0 px-0'}
        `}>
          {sidebarOpen && (
            <FilePanel
              files={files}
              setFiles={setFiles}
              onFilesUploaded={fetchFiles}
            />
          )}
        </aside>

        {/* Chat */}
        <main className="flex-1 overflow-hidden">
          <ChatPanel hasFiles={files.length > 0} />
        </main>
      </div>
    </div>
  )
}
