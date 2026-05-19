<template>
  <div class="max-w-5xl mx-auto space-y-12">
    <header class="flex flex-col md:flex-row md:items-end justify-between gap-6 px-2">
      <div>
        <h1 class="text-3xl lg:text-5xl font-black text-white tracking-tighter">API Keys</h1>
        <p class="text-neutral-500 mt-2 font-bold uppercase tracking-[0.2em] text-[10px] lg:text-xs">Quản lý các khóa truy cập hệ thống</p>
      </div>
      <button 
        @click="openAddModal"
        class="btn-gold px-6 lg:px-8 py-3 lg:py-4 rounded-2xl flex items-center justify-center gap-3 w-full md:w-auto"
      >
        <Plus class="w-5 h-5 lg:w-6 lg:h-6" />
        <span class="text-base lg:text-lg">Tạo Key Mới</span>
      </button>
    </header>

    <!-- Stats Card -->
    <div class="glass-card p-6 lg:p-10 flex flex-col md:flex-row items-center gap-6 lg:gap-10">
      <div class="p-4 lg:p-6 bg-yellow-500/10 rounded-[24px] lg:rounded-[32px] shadow-inner">
        <KeyIcon class="w-10 h-10 lg:w-12 lg:h-12 text-yellow-500" />
      </div>
      <div class="text-center md:text-left">
        <div class="text-3xl lg:text-5xl font-black text-white tabular-nums">{{ keysStore.keys.length }}</div>
        <div class="text-neutral-500 font-bold uppercase tracking-widest text-[10px] lg:text-xs mt-1">Tổng số API Keys hiện có</div>
      </div>
    </div>

    <!-- Keys List -->
    <div v-if="keysStore.loading" class="py-20 text-center">
      <Loader2 class="w-12 h-12 text-yellow-500 animate-spin mx-auto mb-4" />
      <p class="text-neutral-500 font-bold uppercase tracking-widest text-xs">Đang truy xuất dữ liệu...</p>
    </div>

    <div v-else-if="keysStore.keys.length === 0" class="glass-card py-32 text-center">
      <div class="w-20 h-20 bg-white/[0.03] rounded-full flex items-center justify-center mx-auto mb-6">
        <KeyIcon class="w-10 h-10 text-neutral-700" />
      </div>
      <p class="text-neutral-500 font-bold text-lg">Chưa có API key nào được khởi tạo.</p>
      <button @click="openAddModal" class="mt-4 text-yellow-500 font-bold hover:underline">Tạo cái đầu tiên ngay</button>
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-20">
      <div 
        v-for="key in keysStore.keys" 
        :key="key.key"
        class="glass-card p-8 group hover:bg-white/[0.06] transition-all duration-500"
      >
        <div class="flex items-start justify-between mb-8">
          <div class="flex items-center gap-4">
            <div class="p-3 bg-white/[0.03] rounded-2xl group-hover:bg-yellow-500/10 transition-colors">
              <KeyIcon class="w-6 h-6 text-neutral-400 group-hover:text-yellow-500" />
            </div>
            <div>
              <h3 class="text-xl font-black text-white tracking-tight">{{ key.name }}</h3>
              <div class="flex items-center gap-2 text-neutral-500 mt-1">
                <Calendar class="w-3.5 h-3.5" />
                <span class="text-[10px] font-bold uppercase tracking-wider">{{ key.created_at }}</span>
              </div>
            </div>
          </div>
          <div class="flex gap-2">
            <button @click="copyKey(key.key)" class="p-2.5 text-neutral-500 hover:text-white hover:bg-white/10 rounded-xl transition-all"><Copy class="w-5 h-5" /></button>
            <button @click="openEditModal(key)" class="p-2.5 text-neutral-500 hover:text-yellow-500 hover:bg-yellow-500/10 rounded-xl transition-all"><Edit3 class="w-5 h-5" /></button>
            <button @click="handleDelete(key.key)" class="p-2.5 text-neutral-500 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all"><Trash2 class="w-5 h-5" /></button>
          </div>
        </div>

        <div class="space-y-4">
          <div class="p-4 bg-black/40 rounded-2xl border border-white/[0.03] font-mono text-sm break-all text-yellow-500/80">
            {{ maskKey(key.key) }}
          </div>
          <p class="text-sm text-neutral-400 leading-relaxed">{{ key.description || 'Không có mô tả cho key này.' }}</p>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 z-[110] flex items-center justify-center modal-backdrop p-4">
      <div class="w-full max-w-xl glass-card animate-scale-in">
        <div class="p-8 border-b border-white/[0.05] flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="p-3 bg-yellow-500/10 rounded-2xl"><KeyIcon class="w-6 h-6 text-yellow-500" /></div>
            <div>
              <h3 class="text-2xl font-black text-white tracking-tight">{{ isEditing ? 'Cập nhật Key' : 'Tạo Key Mới' }}</h3>
              <p class="text-xs text-neutral-500 font-bold uppercase tracking-widest mt-1">Cấu hình định danh truy cập</p>
            </div>
          </div>
          <button @click="showModal = false" class="text-neutral-500 hover:text-white transition-transform hover:rotate-90"><X class="w-8 h-8" /></button>
        </div>

        <div class="p-8 space-y-8">
          <div class="space-y-3">
            <label class="block text-[10px] font-black text-neutral-500 ml-1 uppercase tracking-[0.2em]">Tên gợi nhớ</label>
            <input v-model="modalData.name" type="text" class="w-full glass-input p-4" placeholder="Ví dụ: Dev Server Key">
          </div>
          <div class="space-y-3">
            <label class="block text-[10px] font-black text-neutral-500 ml-1 uppercase tracking-[0.2em]">Mô tả chi tiết</label>
            <textarea v-model="modalData.description" class="w-full glass-input p-4 min-h-[120px] resize-none" placeholder="Key này dùng cho mục đích gì..."></textarea>
          </div>
        </div>

        <div class="p-8 border-t border-white/[0.05] flex justify-end gap-4">
          <button @click="showModal = false" class="px-8 py-4 rounded-2xl bg-white/[0.03] text-white hover:bg-white/[0.08] font-bold transition-all">Hủy</button>
          <button @click="handleSubmit" :disabled="submitting" class="btn-gold px-10 py-4 rounded-2xl flex items-center gap-2">
            <Loader2 v-if="submitting" class="w-5 h-5 animate-spin" />
            <Save v-else class="w-5 h-5" />
            <span>{{ isEditing ? 'Cập nhật' : 'Khởi tạo ngay' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { 
  Key as KeyIcon, Plus, Loader2, Info, Calendar, 
  Copy, Edit3, Trash2, X, Save 
} from 'lucide-vue-next'
import { useKeysStore, ApiKey } from '@/stores/keysStore'
import { useUIStore } from '@/stores/uiStore'

const keysStore = useKeysStore()
const uiStore = useUIStore()
const showModal = ref(false)
const isEditing = ref(false)
const submitting = ref(false)

const modalData = reactive({
  key: '',
  name: '',
  description: ''
})

onMounted(() => {
  keysStore.loadKeys()
})

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString(undefined, { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  })
}

const maskKey = (key: string) => {
  if (!key) return ''
  if (key.length <= 8) return '****' + key.slice(-2)
  const half = Math.floor(key.length / 2)
  return key.slice(0, half) + '*'.repeat(key.length - half)
}

const openAddModal = () => {
  isEditing.value = false
  modalData.key = ''
  modalData.name = ''
  modalData.description = ''
  showModal.value = true
}

const openEditModal = (key: ApiKey) => {
  isEditing.value = true
  modalData.key = key.key
  modalData.name = key.name
  modalData.description = key.description
  showModal.value = true
}

const handleSubmit = async () => {
  if (!modalData.name) return
  
  submitting.value = true
  let result
  if (isEditing.value) {
    result = await keysStore.updateKey(modalData.key, modalData.name, modalData.description)
  } else {
    result = await keysStore.createKey(modalData.name, modalData.description)
  }
  
  if (result?.success) {
    uiStore.showAlert(isEditing.value ? 'Đã cập nhật API Key' : 'Tạo API Key thành công', 'success')
    showModal.value = false
  } else {
    uiStore.showAlert(result?.message || 'Thao tác thất bại', 'error')
  }
  submitting.value = false
}

const handleDelete = async (key: string) => {
  if (confirm('Bạn có chắc chắn muốn xóa API key này không? Hành động này không thể hoàn tác.')) {
    const result = await keysStore.deleteKey(key)
    if (result && !result.success) {
      uiStore.showAlert(result.message, 'error')
    } else {
      uiStore.showAlert('Đã xóa API Key', 'success')
    }
  }
}

const copyKey = (key: string) => {
  navigator.clipboard.writeText(key).then(() => {
    uiStore.showAlert('Đã sao chép API Key vào bộ nhớ tạm', 'success')
  })
}
</script>
