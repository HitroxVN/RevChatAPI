import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('auth_token'))
  const user = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  async function login(password: string) {
    try {
      const response = await fetch('/api/admin/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password })
      })
      
      const data = await response.json()
      if (data.access_token) {
        token.value = data.access_token
        localStorage.setItem('auth_token', data.access_token)
        return { success: true }
      }
      return { success: false, message: data.detail || 'Đăng nhập thất bại' }
    } catch (error) {
      return { success: false, message: 'Lỗi kết nối máy chủ' }
    }
  }

  function logout() {
    token.value = null
    localStorage.removeItem('auth_token')
  }

  return {
    token,
    user,
    isLoggedIn,
    login,
    logout
  }
})
