import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 60000,
})

export const uploadFiles = async (files) => {
  const formData = new FormData()
  files.forEach(file => formData.append('files', file))
  const res = await api.post('/api/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return res.data
}

export const sendMessage = async (question, fileIds = null, topK = 5) => {
  const res = await api.post('/api/chat', {
    question,
    file_ids: fileIds,
    top_k: topK,
  })
  return res.data
}

export const listFiles = async () => {
  const res = await api.get('/api/files')
  return res.data
}

export const deleteFile = async (fileId) => {
  const res = await api.delete(`/api/files/${fileId}`)
  return res.data
}

export const healthCheck = async () => {
  const res = await api.get('/health')
  return res.data
}
