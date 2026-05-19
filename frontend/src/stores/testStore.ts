import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTestStore = defineStore('test', () => {
  const models = ref<string[]>([])
  const loadingModels = ref(false)
  const executing = ref(false)
  const lastResponse = ref<any>(null)
  const lastStatus = ref<number | null>(null)
  const lastStatusText = ref('')

  async function loadModels() {
    loadingModels.value = true
    try {
      const response = await fetch('/v1/models')
      const data = await response.json()
      if (data.data) {
        models.value = data.data.map((m: any) => m.id)
      }
    } catch (error) {
      console.error('Failed to load models:', error)
    } finally {
      loadingModels.value = false
    }
  }

  async function sendTestMessage(apiKey: string, model: string, message: string) {
    executing.value = true
    lastResponse.value = 'Đang chờ phản hồi...'
    lastStatus.value = null
    
    try {
      const response = await fetch('/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
          model,
          messages: [{ role: 'user', content: message }]
        })
      })

      lastStatus.value = response.status
      lastStatusText.value = response.statusText
      const data = await response.json()
      lastResponse.value = data
      return { success: response.ok, status: response.status }
    } catch (error: any) {
      lastResponse.value = { error: error.message }
      return { success: false, message: error.message }
    } finally {
      executing.value = false
    }
  }

  return {
    models,
    loadingModels,
    executing,
    lastResponse,
    lastStatus,
    lastStatusText,
    loadModels,
    sendTestMessage
  }
})
