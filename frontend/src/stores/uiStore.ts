import { defineStore } from 'pinia'
import { ref } from 'vue'

export type AlertType = 'success' | 'error' | 'info' | 'warning'

export interface Alert {
  id: number
  message: string
  type: AlertType
  timeout?: number
}

export const useUIStore = defineStore('ui', () => {
  const alerts = ref<Alert[]>([])
  let nextId = 0

  function showAlert(message: string, type: AlertType = 'info', timeout = 3000) {
    const id = nextId++
    alerts.value.push({ id, message, type, timeout })

    if (timeout > 0) {
      setTimeout(() => {
        removeAlert(id)
      }, timeout)
    }
  }

  function removeAlert(id: number) {
    const index = alerts.value.findIndex(a => a.id === id)
    if (index !== -1) {
      alerts.value.splice(index, 1)
    }
  }

  return {
    alerts,
    showAlert,
    removeAlert
  }
})
