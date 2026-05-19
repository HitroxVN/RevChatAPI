import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './authStore'

export interface ChatXAccount {
  id: string
  email: string
  auto_clear_history: boolean
  note?: string
  is_failed?: boolean
}

export interface EaseMateAccount {
  id: string
  device_uuid: string
  identity_id: string
  token?: string
  note?: string
  is_failed?: boolean
}

export const useAccountsStore = defineStore('accounts', () => {
  const chatxAccounts = ref<ChatXAccount[]>([])
  const easemateAccounts = ref<EaseMateAccount[]>([])
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

  async function loadAllAccounts() {
    loading.value = true
    try {
      const [chatxRes, easemateRes] = await Promise.all([
        apiFetch('/chatx/accounts'),
        apiFetch('/easemate/accounts')
      ])
      
      if (chatxRes) {
        const data = await chatxRes.json()
        chatxAccounts.value = data.accounts || []
      }
      
      if (easemateRes) {
        const data = await easemateRes.json()
        easemateAccounts.value = data.accounts || []
      }
    } catch (error) {
      console.error('Failed to load accounts:', error)
    } finally {
      loading.value = false
    }
  }

  async function saveChatXAccount(payload: { id?: string | null, email: string, password?: string, auto_clear_history: boolean, note?: string }) {
    try {
      const response = await apiFetch('/chatx/account/save', {
        method: 'POST',
        body: JSON.stringify(payload)
      })
      if (response) {
        const data = await response.json()
        if (data.success) {
          await loadAllAccounts()
          return { success: true }
        }
        return { success: false, message: data.message }
      }
    } catch (error) {
      return { success: false, message: 'Lỗi kết nối' }
    }
  }

  async function saveEaseMateAccount(payload: { id?: string | null, device_uuid: string, identity_id: string, token?: string, note?: string }) {
    try {
      const response = await apiFetch('/easemate/account/save', {
        method: 'POST',
        body: JSON.stringify(payload)
      })
      if (response) {
        const data = await response.json()
        if (data.success) {
          await loadAllAccounts()
          return { success: true }
        }
        return { success: false, message: data.message }
      }
    } catch (error) {
      return { success: false, message: 'Lỗi kết nối' }
    }
  }

  async function deleteAccount(provider: 'chatx' | 'easemate', id: string) {
    try {
      const response = await apiFetch(`/${provider}/account/delete`, {
        method: 'POST',
        body: JSON.stringify({ id })
      })
      if (response) {
        const data = await response.json()
        if (data.success) {
          await loadAllAccounts()
          return { success: true }
        }
        return { success: false, message: data.message }
      }
    } catch (error) {
      return { success: false, message: 'Lỗi kết nối' }
    }
  }

  async function verifyEaseMate(device_uuid: string, identity_id: string, token?: string) {
    try {
      const response = await apiFetch('/easemate/account/verify', {
        method: 'POST',
        body: JSON.stringify({ device_uuid, identity_id, token })
      })
      if (response) {
        return await response.json()
      }
    } catch (error) {
      return { success: false, message: 'Lỗi kết nối' }
    }
  }

  async function getEaseMateScript() {
    try {
      const response = await apiFetch('/easemate/script')
      if (response) {
        return await response.json()
      }
    } catch (error) {
      return { success: false, message: 'Lỗi kết nối' }
    }
  }

  return {
    chatxAccounts,
    easemateAccounts,
    loading,
    loadAllAccounts,
    saveChatXAccount,
    saveEaseMateAccount,
    deleteAccount,
    verifyEaseMate,
    getEaseMateScript
  }
})
