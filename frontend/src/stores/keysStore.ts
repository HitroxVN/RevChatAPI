import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './authStore'

export interface ApiKey {
  key: string
  name: string
  description: string
  created_at: string
}

export const useKeysStore = defineStore('keys', () => {
  const keys = ref<ApiKey[]>([])
  const loading = ref(false)
  const authStore = useAuthStore()

  async function apiFetch(endpoint: string, options: RequestInit = {}) {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authStore.token}`,
      ...options.headers,
    }

    const response = await fetch(`/api/admin${endpoint}`, { ...options, headers })
    if (response.status === 401) {
      authStore.logout()
      window.location.href = '/login'
      return null
    }
    return response
  }

  async function loadKeys() {
    loading.value = true
    try {
      const response = await apiFetch('/keys')
      if (response) {
        const data = await response.json()
        keys.value = data.keys || []
      }
    } catch (error) {
      console.error('Failed to load keys:', error)
    } finally {
      loading.value = false
    }
  }

  async function createKey(name: string, description: string) {
    try {
      const response = await apiFetch('/keys/create', {
        method: 'POST',
        body: JSON.stringify({ name, description })
      })
      if (response) {
        const data = await response.json()
        if (data.success) {
          await loadKeys()
          return { success: true }
        }
        return { success: false, message: data.message }
      }
    } catch (error) {
      return { success: false, message: 'Lỗi kết nối' }
    }
  }

  async function updateKey(key: string, name: string, description: string) {
    try {
      const response = await apiFetch('/keys/update', {
        method: 'POST',
        body: JSON.stringify({ key, name, description })
      })
      if (response) {
        const data = await response.json()
        if (data.success) {
          await loadKeys()
          return { success: true }
        }
        return { success: false, message: data.message }
      }
    } catch (error) {
      return { success: false, message: 'Lỗi kết nối' }
    }
  }

  async function deleteKey(key: string) {
    try {
      const response = await apiFetch('/keys/delete', {
        method: 'POST',
        body: JSON.stringify({ key })
      })
      if (response) {
        const data = await response.json()
        if (data.success) {
          await loadKeys()
          return { success: true }
        }
        return { success: false, message: data.message }
      }
    } catch (error) {
      return { success: false, message: 'Lỗi kết nối' }
    }
  }

  return {
    keys,
    loading,
    loadKeys,
    createKey,
    updateKey,
    deleteKey
  }
})
