<template>
  <div class="max-w-6xl mx-auto space-y-12">
    <header class="px-2">
      <h1 class="text-5xl font-black text-white tracking-tighter">Test API</h1>
      <p class="text-neutral-500 mt-2 font-bold uppercase tracking-[0.2em] text-xs">Thử nghiệm các mô hình AI trong thời gian thực</p>
    </header>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-10">
      <!-- Request Panel -->
      <div class="lg:col-span-5 space-y-8 animate-slide-right">
        <div class="glass-card p-10 space-y-8">
          <div class="space-y-3">
            <label class="block text-[10px] font-black text-neutral-500 ml-1 uppercase tracking-[0.2em]">Lựa chọn API Key</label>
            <div class="relative group">
              <Key class="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-500 group-focus-within:text-yellow-500 transition-colors" />
              <select v-model="selectedKey" class="w-full glass-input py-5 pl-14 pr-12 text-base appearance-none cursor-pointer">
                <option value="" class="bg-neutral-900 text-white">Chọn một API key...</option>
                <option v-for="key in keysStore.keys" :key="key.key" :value="key.key" class="bg-neutral-900 text-white">
                  {{ key.name }} ({{ key.key.substring(0, 12) }}...)
                </option>
              </select>
              <div class="absolute right-5 top-1/2 -translate-y-1/2 pointer-events-none text-neutral-600">
                <ChevronDown class="w-6 h-6" />
              </div>
            </div>
          </div>

          <div class="space-y-3">
            <label class="block text-[10px] font-black text-neutral-500 ml-1 uppercase tracking-[0.2em]">AI Model</label>
            <div class="relative group">
              <Cpu class="absolute left-5 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-500 group-focus-within:text-blue-500 transition-colors" />
              <select v-model="selectedModel" class="w-full glass-input py-5 pl-14 pr-12 text-base appearance-none cursor-pointer font-mono" :disabled="testStore.loadingModels">
                <option v-for="model in testStore.models" :key="model" :value="model" class="bg-neutral-900 text-white">{{ model }}</option>
              </select>
              <div class="absolute right-5 top-1/2 -translate-y-1/2 pointer-events-none text-neutral-600">
                <Loader2 v-if="testStore.loadingModels" class="w-5 h-5 animate-spin" />
                <ChevronDown v-else class="w-6 h-6" />
              </div>
            </div>
          </div>

          <div class="space-y-3">
            <label class="block text-[10px] font-black text-neutral-500 ml-1 uppercase tracking-[0.2em]">Tin nhắn (User Prompt)</label>
            <textarea 
              v-model="message"
              class="w-full glass-input p-6 min-h-[220px] resize-none text-lg leading-relaxed" 
              placeholder="Bạn muốn hỏi AI điều gì?"
            ></textarea>
          </div>

          <button 
            @click="handleSend"
            :disabled="testStore.executing || !selectedKey || !message"
            class="w-full btn-gold py-6 rounded-[24px] text-2xl font-black shadow-2xl flex items-center justify-center gap-4 disabled:opacity-30"
          >
            <Loader2 v-if="testStore.executing" class="w-8 h-8 animate-spin" />
            <Zap v-else class="w-8 h-8 fill-current" />
            <span>{{ testStore.executing ? 'ĐANG XỬ LÝ...' : 'THỰC THI' }}</span>
          </button>
        </div>
      </div>

      <!-- Response Panel -->
      <div class="lg:col-span-7 space-y-6 animate-slide-left">
        <div class="flex items-center justify-between px-2">
          <div class="flex items-center gap-3">
            <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <label class="text-[10px] font-black text-neutral-500 uppercase tracking-[0.2em]">Console Output</label>
          </div>
          <div 
            v-if="testStore.lastStatus"
            class="px-4 py-1.5 rounded-full text-[10px] font-black tracking-widest uppercase border"
            :class="testStore.lastStatus < 400 ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'"
          >
            HTTP {{ testStore.lastStatus }} {{ testStore.lastStatusText }}
          </div>
        </div>
        
        <div class="glass-card p-1 min-h-[620px] bg-black/40 flex flex-col">
          <div class="flex items-center gap-2 p-4 border-b border-white/[0.05]">
            <div class="w-3 h-3 rounded-full bg-red-500/20"></div>
            <div class="w-3 h-3 rounded-full bg-yellow-500/20"></div>
            <div class="w-3 h-3 rounded-full bg-green-500/20"></div>
          </div>
          <div class="flex-1 p-8 font-mono text-sm overflow-auto max-h-[700px] relative custom-scrollbar">
            <pre 
              class="whitespace-pre-wrap break-all selection:bg-yellow-500 selection:text-black"
              :class="{
                'text-neutral-600': !testStore.lastResponse || testStore.executing,
                'text-green-400/90': testStore.lastStatus && testStore.lastStatus < 400,
                'text-red-400/90': testStore.lastStatus && testStore.lastStatus >= 400
              }"
            >{{ formattedResponse }}</pre>
            
            <div v-if="!testStore.lastResponse && !testStore.executing" class="absolute inset-0 flex flex-col items-center justify-center opacity-20 group">
              <MessageSquare class="w-24 h-24 mb-6 text-neutral-500 group-hover:scale-110 transition-transform duration-700" />
              <p class="font-black uppercase tracking-[0.4em] text-sm text-neutral-500">Waiting for request</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { Zap, Loader2, MessageSquare, ChevronDown, Key, Cpu } from 'lucide-vue-next'
import { useTestStore } from '@/stores/testStore'
import { useKeysStore } from '@/stores/keysStore'

const testStore = useTestStore()
const keysStore = useKeysStore()

const selectedKey = ref('')
const selectedModel = ref('gpt-4o-mini')
const message = ref('')

watch(() => testStore.models, (newModels) => {
  if (newModels.length > 0) {
    if (!selectedModel.value || !newModels.includes(selectedModel.value)) {
      selectedModel.value = newModels[0]
    }
  }
}, { immediate: true })

onMounted(async () => {
  await testStore.loadModels()
  keysStore.loadKeys()
})

const formattedResponse = computed(() => {
  if (!testStore.lastResponse) return ''
  if (typeof testStore.lastResponse === 'string') return testStore.lastResponse
  return JSON.stringify(testStore.lastResponse, null, 2)
})

const handleSend = async () => {
  if (!selectedKey.value || !message.value) return
  await testStore.sendTestMessage(selectedKey.value, selectedModel.value, message.value)
}
</script>
