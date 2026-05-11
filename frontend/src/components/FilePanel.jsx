import { useState, useRef, useCallback } from 'react'
import { Upload, File, Trash2, CheckCircle, XCircle, Loader2, FileText, FileSpreadsheet, FileImage, Presentation } from 'lucide-react'
import { uploadFiles, deleteFile } from '../api'

const FILE_ICONS = {
  '.pdf': FileText,
  '.docx': FileText, '.doc': FileText,
  '.xlsx': FileSpreadsheet, '.xls': FileSpreadsheet, '.csv': FileSpreadsheet,
  '.pptx': Presentation, '.ppt': Presentation,
  '.png': FileImage, '.jpg': FileImage, '.jpeg': FileImage,
  '.txt': FileText, '.md': FileText,
}

const FileIcon = ({ type }) => {
  const Icon = FILE_ICONS[type] || File
  return <Icon size={14} />
}

const formatBytes = (bytes) => {
  if (!bytes) return '—'
  if (bytes < 1024) return `${bytes}B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`
}

export default function FilePanel({ files, setFiles, onFilesUploaded }) {
  const [dragging, setDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadResults, setUploadResults] = useState([])
  const inputRef = useRef()

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const dropped = Array.from(e.dataTransfer.files)
    if (dropped.length) handleUpload(dropped)
  }, [])

  const handleUpload = async (selectedFiles) => {
    setUploading(true)
    setUploadResults([])
    try {
      const results = await uploadFiles(selectedFiles)
      setUploadResults(results)
      const successful = results.filter(r => r.success)
      if (successful.length > 0) onFilesUploaded()
    } catch (err) {
      setUploadResults([{ success: false, error: 'Upload failed. Is the backend running?', filename: 'unknown' }])
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (fileId, filename) => {
    try {
      await deleteFile(fileId)
      setFiles(prev => prev.filter(f => f.file_id !== fileId))
    } catch (err) {
      console.error('Delete failed', err)
    }
  }

  return (
    <div className="flex flex-col h-full gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="font-display font-semibold text-ink-100 text-sm tracking-wide uppercase">
          Documents
        </h2>
        <span className="tag">{files.length} files</span>
      </div>

      {/* Drop Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`
          relative border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer
          transition-all duration-300 group
          ${dragging
            ? 'border-accent bg-accent/5 scale-[1.02]'
            : 'border-ink-700 hover:border-ink-500 hover:bg-ink-800/30'
          }
        `}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          className="hidden"
          accept=".pdf,.docx,.doc,.pptx,.ppt,.xlsx,.xls,.csv,.txt,.md,.json,.xml,.html,.png,.jpg,.jpeg"
          onChange={(e) => handleUpload(Array.from(e.target.files))}
        />

        <div className={`
          w-10 h-10 rounded-xl mx-auto mb-3 flex items-center justify-center
          transition-all duration-300
          ${dragging ? 'bg-accent text-ink-950' : 'bg-ink-800 text-ink-400 group-hover:bg-ink-700 group-hover:text-ink-200'}
        `}>
          {uploading ? <Loader2 size={18} className="animate-spin" /> : <Upload size={18} />}
        </div>

        <p className="text-ink-300 text-sm font-body">
          {uploading ? 'Processing files...' : 'Drop files or click to upload'}
        </p>
        <p className="text-ink-600 text-xs mt-1 font-mono">
          PDF · DOCX · PPTX · XLSX · CSV · TXT · Images
        </p>
      </div>

      {/* Upload Results */}
      {uploadResults.length > 0 && (
        <div className="space-y-1.5 animate-fade-in">
          {uploadResults.map((r, i) => (
            <div key={i} className={`
              flex items-start gap-2.5 p-3 rounded-xl text-xs font-body
              ${r.success ? 'bg-emerald-950/40 border border-emerald-800/30' : 'bg-red-950/40 border border-red-800/30'}
            `}>
              {r.success
                ? <CheckCircle size={14} className="text-emerald-400 mt-0.5 shrink-0" />
                : <XCircle size={14} className="text-red-400 mt-0.5 shrink-0" />
              }
              <div>
                <p className={r.success ? 'text-emerald-300' : 'text-red-300'}>
                  {r.success ? `${r.chunks_created} chunks indexed` : r.error}
                </p>
                <p className="text-ink-500 truncate max-w-[160px]">{r.filename}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* File List */}
      <div className="flex-1 overflow-y-auto space-y-1.5 min-h-0">
        {files.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-ink-600 text-sm">No documents yet</p>
            <p className="text-ink-700 text-xs mt-1">Upload files to start chatting</p>
          </div>
        ) : (
          files.map((file) => (
            <div
              key={file.file_id}
              className="group flex items-center gap-3 p-3 rounded-xl glass-light hover:border-ink-600 transition-all duration-200 animate-slide-in"
            >
              <div className="w-8 h-8 rounded-lg bg-ink-800 flex items-center justify-center text-accent shrink-0">
                <FileIcon type={file.file_type} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-ink-200 text-xs font-body truncate">{file.filename}</p>
                <p className="text-ink-600 text-xs font-mono mt-0.5">
                  {file.chunks} chunks · {formatBytes(file.size_bytes)}
                </p>
              </div>
              <button
                onClick={() => handleDelete(file.file_id, file.filename)}
                className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg hover:bg-red-900/40 hover:text-red-400 text-ink-600 transition-all duration-200"
              >
                <Trash2 size={13} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
