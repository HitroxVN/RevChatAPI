<template>
  <div class="fixed top-6 right-6 z-[200] flex flex-col gap-4 pointer-events-none">
    <transition-group name="alert">
      <div 
        v-for="alert in uiStore.alerts" 
        :key="alert.id"
        class="pointer-events-auto flex items-center gap-3 px-6 py-4 rounded-2xl shadow-2xl border backdrop-blur-xl min-w-[300px] max-w-md animate-slide-in"
        :class="alertClass(alert.type)"
      >
        <component :is="alertIcon(alert.type)" class="w-6 h-6 flex-shrink-0" />
        <span class="font-bold text-sm leading-tight">{{ alert.message }}</span>
        <button 
          @click="uiStore.removeAlert(alert.id)"
          class="ml-auto p-1 hover:bg-white/10 rounded-lg transition-colors"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { 
  CheckCircle2, AlertCircle, Info, AlertTriangle, X 
} from 'lucide-vue-next'
import { useUIStore, AlertType } from '@/stores/uiStore'

const uiStore = useUIStore()

const alertClass = (type: AlertType) => {
  switch (type) {
    case 'success':
      return 'bg-green-500/10 border-green-500/20 text-green-400'
    case 'error':
      return 'bg-red-500/10 border-red-500/20 text-red-400'
    case 'warning':
      return 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400'
    default:
      return 'bg-blue-500/10 border-blue-500/20 text-blue-400'
  }
}

const alertIcon = (type: AlertType) => {
  switch (type) {
    case 'success':
      return CheckCircle2
    case 'error':
      return AlertCircle
    case 'warning':
      return AlertTriangle
    default:
      return Info
  }
}
</script>

<style scoped>
.alert-enter-active,
.alert-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.alert-enter-from {
  opacity: 0;
  transform: translateX(30px) scale(0.9);
}

.alert-leave-to {
  opacity: 0;
  transform: translateX(30px) scale(0.9);
}

.animate-slide-in {
  animation: slide-in 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>
