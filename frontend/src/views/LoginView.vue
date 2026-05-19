<template>
  <div class="min-h-screen bg-[#050505] flex items-center justify-center p-6 relative overflow-hidden">
    <!-- Vibrant Background Blobs -->
    <div class="vibrant-blob w-[600px] h-[600px] bg-yellow-500/10 -top-48 -left-24"></div>
    <div class="vibrant-blob w-[500px] h-[500px] bg-blue-600/10 -bottom-48 -right-24"></div>

    <div class="w-full max-w-md relative z-10 animate-fade-in">
      <div class="text-center mb-12">
        <div class="inline-block w-24 h-24 bg-white/5 rounded-[32px] mb-6 shadow-[0_0_30px_rgba(255,255,255,0.05)] border border-white/10 overflow-hidden animate-bounce-slow">
          <img src="/logo.png" alt="Logo" class="w-full h-full object-contain p-2" />
        </div>
        <h1 class="text-6xl font-black text-white tracking-tighter mb-2">RevChat</h1>
        <p class="text-neutral-500 font-bold uppercase tracking-[0.3em] text-xs">Hệ thống Quản trị</p>
      </div>

      <div class="glass-card p-10 shadow-2xl">
        <div class="space-y-8">
          <div class="space-y-3">
            <label class="block text-[10px] font-black text-neutral-500 ml-1 uppercase tracking-[0.2em]">Admin Authentication</label>
            <div class="relative group">
              <Lock class="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-500 group-focus-within:text-yellow-500 transition-colors" />
              <input 
                v-model="password"
                type="password" 
                class="w-full glass-input py-5 pl-14 pr-5 text-lg" 
                placeholder="Nhập Admin Key..."
                @keyup.enter="handleLogin"
              >
            </div>
          </div>

          <button 
            @click="handleLogin"
            :disabled="loading"
            class="w-full btn-gold py-5 rounded-[24px] text-xl font-black shadow-xl flex items-center justify-center gap-3 disabled:opacity-50"
          >
            <template v-if="loading">
              <Loader2 class="w-6 h-6 animate-spin" />
              <span class="tracking-tight">ĐANG XÁC THỰC...</span>
            </template>
            <template v-else>
              <span class="tracking-tight font-black">TIẾP TỤC</span>
              <ChevronRight class="w-6 h-6" />
            </template>
          </button>

          <div v-if="errorMessage" class="text-red-400 text-center font-bold text-sm bg-red-500/10 py-3 rounded-xl border border-red-500/20 animate-shake">
            {{ errorMessage }}
          </div>
        </div>
      </div>
      
      <p class="text-center text-neutral-600 text-[10px] mt-8 font-bold uppercase tracking-widest">
        &copy; 2024 REVChat API &bull; Version 2.0
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Zap, User, Lock, ChevronRight, Loader2 } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  if (!password.value) {
    errorMessage.value = 'Vui lòng nhập Admin Key'
    return
  }

  loading.value = true
  errorMessage.value = ''
  
  const result = await authStore.login(password.value)
  
  if (result.success) {
    router.push('/keys')
  } else {
    errorMessage.value = result.message || 'Xác thực thất bại'
  }
  
  loading.value = false
}
</script>
