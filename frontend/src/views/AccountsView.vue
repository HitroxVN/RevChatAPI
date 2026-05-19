<template>
  <div class="max-w-5xl mx-auto space-y-12">
    <header class="px-2">
      <h1 class="text-5xl font-black text-white tracking-tighter">Tài khoản</h1>
      <p class="text-neutral-500 mt-2 font-bold uppercase tracking-[0.2em] text-xs">Quản lý định danh các nhà cung cấp AI</p>
    </header>

    <!-- Provider Selection -->
    <div v-if="!currentProvider" class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- ChatX Provider Card -->
      <div 
        @click="currentProvider = 'chatx'" 
        class="glass-card p-12 cursor-pointer group hover:bg-white/[0.06] transition-all duration-500 border-white/[0.05] hover:border-yellow-500/30"
      >
        <div class="flex items-center justify-between mb-10">
          <div class="p-5 bg-yellow-500/10 rounded-[32px] group-hover:scale-110 transition-transform duration-500">
            <ShieldCheck class="w-12 h-12 text-yellow-500" />
          </div>
          <div class="text-neutral-600 group-hover:text-yellow-500 transition-colors">
            <ChevronRight class="w-10 h-10" />
          </div>
        </div>
        <h3 class="text-3xl font-black text-white tracking-tight">ChatX Provider</h3>
        <p class="text-neutral-500 mt-4 font-medium leading-relaxed">Quản lý các tài khoản ChatX.</p>
      </div>

      <!-- EaseMate Provider Card -->
      <div 
        @click="currentProvider = 'easemate'" 
        class="glass-card p-12 cursor-pointer group hover:bg-white/[0.06] transition-all duration-500 border-white/[0.05] hover:border-blue-500/30"
      >
        <div class="flex items-center justify-between mb-10">
          <div class="p-5 bg-blue-500/10 rounded-[32px] group-hover:scale-110 transition-transform duration-500">
            <Cpu class="w-12 h-12 text-blue-500" />
          </div>
          <div class="text-neutral-600 group-hover:text-blue-500 transition-colors">
            <ChevronRight class="w-10 h-10" />
          </div>
        </div>
        <h3 class="text-3xl font-black text-white tracking-tight">EaseMate Provider</h3>
        <p class="text-neutral-500 mt-4 font-medium leading-relaxed">Cấu hình Device UUID và Identity ID cho các model EaseMate.</p>
      </div>
    </div>

    <!-- Account List View -->
    <div v-else class="space-y-8 animate-fade-in">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 px-2">
        <div class="flex items-center gap-6">
          <button 
            @click="currentProvider = null" 
            class="p-4 bg-white/[0.03] hover:bg-white/[0.08] text-white rounded-[24px] transition-all border border-white/[0.05]"
          >
            <ArrowLeft class="w-6 h-6" />
          </button>
          <div>
            <h2 class="text-4xl font-black text-white tracking-tight">
              {{ currentProvider === 'chatx' ? 'ChatX Accounts' : 'EaseMate Accounts' }}
            </h2>
            <p class="text-neutral-500 text-xs font-bold uppercase tracking-widest mt-1">
              {{ currentProvider === 'chatx' ? 'Danh sách tài khoản Email/Password' : 'Danh sách Device UUID và Identity ID' }}
            </p>
          </div>
        </div>
        <button 
          @click="openAddModal"
          class="btn-gold px-8 py-4 rounded-2xl flex items-center gap-3"
        >
          <Plus class="w-6 h-6" />
          <span class="text-lg">Thêm Tài khoản</span>
        </button>
      </div>

      <div v-if="accountsStore.loading" class="py-24 text-center">
        <Loader2 class="w-12 h-12 text-yellow-500 animate-spin mx-auto mb-4" />
        <p class="text-neutral-500 font-bold uppercase tracking-widest text-xs">Đang đồng bộ dữ liệu...</p>
      </div>

      <div v-else-if="currentAccounts.length === 0" class="glass-card py-32 text-center">
        <FolderOpen class="w-16 h-16 mx-auto mb-6 text-neutral-800" />
        <p class="text-neutral-500 font-bold text-lg">Chưa có tài khoản nào được thêm.</p>
        <button @click="openAddModal" class="mt-4 text-yellow-500 font-bold hover:underline">Thêm ngay</button>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6 pb-20">
        <div 
          v-for="acc in currentAccounts" 
          :key="acc.id"
          class="glass-card p-8 group hover:bg-white/[0.06] transition-all duration-500 relative"
          @click="openEditModal(acc)"
        >
          <div class="flex items-center justify-between mb-6">
            <div 
              class="p-4 rounded-2xl group-hover:scale-110 transition-transform duration-500"
              :class="currentProvider === 'chatx' ? 'bg-yellow-500/10' : 'bg-blue-500/10'"
            >
              <ShieldCheck v-if="currentProvider === 'chatx'" class="w-8 h-8 text-yellow-500" />
              <Cpu v-else class="w-8 h-8 text-blue-500" />
            </div>
            <div class="flex items-center gap-2">
              <button 
                @click.stop="handleDelete(acc.id)"
                class="p-2.5 text-neutral-600 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all"
              >
                <Trash2 class="w-5 h-5" />
              </button>
              <div class="p-2.5 text-neutral-600 group-hover:text-white transition-colors">
                <Edit3 class="w-6 h-6" />
              </div>
            </div>
          </div>
          <h3 class="text-2xl font-black text-white tracking-tight">
            {{ currentProvider === 'chatx' ? 'ChatX User' : 'EaseMate Device' }}
          </h3>
          <p class="text-sm font-mono text-neutral-500 mt-2 truncate max-w-full">
            {{ currentProvider === 'chatx' ? (acc as any).email : (acc as any).device_uuid }}
          </p>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 z-[110] flex items-center justify-center modal-backdrop p-4">
      <div class="w-full max-w-2xl glass-card animate-scale-in">
        <!-- Modal Header -->
        <div class="p-8 border-b border-white/[0.05] flex items-center justify-between">
          <div class="flex items-center gap-5">
            <div 
              class="p-4 rounded-2xl"
              :class="currentProvider === 'chatx' ? 'bg-yellow-500/10' : 'bg-blue-500/10'"
            >
              <ShieldCheck v-if="currentProvider === 'chatx'" class="w-8 h-8 text-yellow-500" />
              <Cpu v-else class="w-8 h-8 text-blue-500" />
            </div>
            <div>
              <h3 class="text-2xl font-black text-white tracking-tight">
                {{ isEditing ? 'Cập nhật' : 'Thêm mới' }} {{ currentProvider === 'chatx' ? 'ChatX' : 'EaseMate' }}
              </h3>
              <p class="text-[10px] text-neutral-500 font-bold uppercase tracking-widest mt-1">Cấu hình thông tin nhà cung cấp</p>
            </div>
          </div>
          <button @click="showModal = false" class="text-neutral-500 hover:text-white transition-transform hover:rotate-90">
            <X class="w-10 h-10" />
          </button>
        </div>

        <!-- ChatX Fields -->
        <div v-if="currentProvider === 'chatx'" class="p-8 space-y-8">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="space-y-3">
              <label class="block text-[10px] font-black text-neutral-500 ml-1 uppercase tracking-[0.2em]">Địa chỉ Email</label>
              <input v-model="chatxData.email" type="email" class="w-full glass-input p-5" placeholder="user@example.com">
            </div>
            <div class="space-y-3">
              <label class="block text-[10px] font-black text-neutral-500 ml-1 uppercase tracking-[0.2em]">Mật khẩu mới</label>
              <input v-model="chatxData.password" type="password" class="w-full glass-input p-5" placeholder="••••••••">
            </div>
          </div>
          <div class="flex items-center justify-between p-6 bg-white/[0.03] rounded-[32px] border border-white/[0.05]">
            <div>
              <div class="text-lg font-black text-white tracking-tight">Tự động xóa lịch sử</div>
              <div class="text-xs text-neutral-500 font-medium mt-1">Làm sạch context AI sau mỗi request</div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="chatxData.auto_clear_history" class="sr-only peer">
              <div class="w-16 h-8 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[4px] after:left-[4px] after:bg-white after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-yellow-500 shadow-inner"></div>
            </label>
          </div>
        </div>

        <!-- EaseMate Fields -->
        <div v-if="currentProvider === 'easemate'" class="p-8 space-y-8">
          <div class="flex justify-between items-center bg-blue-500/10 p-5 rounded-[28px] border border-blue-500/20">
            <div class="flex items-center gap-3 text-blue-400">
              <Info class="w-6 h-6" />
              <span class="text-xs font-black uppercase tracking-widest">Hỗ trợ trích xuất ID</span>
            </div>
            <button @click="toggleInstructions" class="px-5 py-2.5 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 text-[10px] font-black uppercase tracking-widest rounded-xl transition-all border border-blue-500/20">
              {{ showInstructions ? 'Đóng' : 'Xem hướng dẫn' }}
            </button>
          </div>

          <transition name="fade">
            <div v-if="showInstructions" class="p-6 bg-black/60 rounded-[32px] border border-white/[0.05] space-y-4">
              <div class="text-xs text-neutral-400 space-y-2 leading-relaxed">
                <p>1. Gửi tin nhắn tại: <a href="https://www.easemate.ai" target="_blank" class="text-blue-400 hover:underline">easemate.ai</a></p>
                <p>2. Mở Console (F12) &rarr; Dán Script &rarr; Enter</p>
                <p>3. Dán kết quả vào các ô bên dưới</p>
              </div>
              <div class="pt-4 border-t border-white/[0.05] flex items-center justify-between">
                <span class="text-[10px] font-black text-blue-500 uppercase tracking-[0.2em]">JS Extraction Script</span>
                <button @click="copyScript" class="flex items-center gap-2 text-[10px] font-black text-neutral-400 hover:text-white bg-white/5 px-4 py-2 rounded-xl transition-all">
                  <Copy class="w-4 h-4" />
                  <span>SAO CHÉP</span>
                </button>
              </div>
              <pre class="p-4 bg-black/40 rounded-2xl border border-white/[0.03] text-[10px] font-mono text-blue-300/50 overflow-x-auto max-h-32">{{ emScript }}</pre>
            </div>
          </transition>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="space-y-3">
              <label class="block text-[10px] font-black text-neutral-500 ml-1 uppercase tracking-[0.2em]">Device UUID</label>
              <input v-model="easemateData.device_uuid" type="text" class="w-full glass-input p-5 font-mono" placeholder="Mã thiết bị">
            </div>
            <div class="space-y-3">
              <label class="block text-[10px] font-black text-neutral-500 ml-1 uppercase tracking-[0.2em]">Identity ID</label>
              <input v-model="easemateData.identity_id" type="text" class="w-full glass-input p-5 font-mono" placeholder="Mã định danh">
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="p-8 border-t border-white/[0.05] flex justify-end gap-4">
          <button @click="showModal = false" class="px-8 py-4 rounded-2xl bg-white/[0.03] text-white hover:bg-white/[0.08] font-bold transition-all">Hủy</button>
          <button 
            v-if="currentProvider === 'easemate'"
            @click="handleVerify"
            :disabled="verifying"
            class="px-8 py-4 rounded-2xl bg-blue-500/10 text-blue-400 hover:bg-blue-500/20 font-bold transition-all border border-blue-500/20 flex items-center gap-2"
          >
            <Loader2 v-if="verifying" class="w-5 h-5 animate-spin" />
            <ShieldCheck v-else class="w-5 h-5" />
            <span>Xác thực</span>
          </button>
          <button @click="handleSave" :disabled="submitting" class="btn-gold px-12 py-4 rounded-2xl flex items-center gap-3">
            <Loader2 v-if="submitting" class="w-6 h-6 animate-spin" />
            <Save v-else class="w-6 h-6" />
            <span class="text-lg">Lưu lại</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import { 
  ShieldCheck, Cpu, ChevronRight, ArrowLeft, Plus, 
  Loader2, FolderOpen, Trash2, Edit3, X, Info, Copy, Save
} from 'lucide-vue-next'
import { useAccountsStore } from '@/stores/accountsStore'
import { useUIStore } from '@/stores/uiStore'

const accountsStore = useAccountsStore()
const uiStore = useUIStore()
const currentProvider = ref<'chatx' | 'easemate' | null>(null)
const showModal = ref(false)
const isEditing = ref(false)
const submitting = ref(false)
const verifying = ref(false)
const showInstructions = ref(false)
const emScript = ref('')

const chatxData = reactive({
  id: null as string | null,
  email: '',
  password: '',
  auto_clear_history: false
})

const easemateData = reactive({
  id: null as string | null,
  device_uuid: '',
  identity_id: ''
})

onMounted(() => {
  accountsStore.loadAllAccounts()
})

const currentAccounts = computed(() => {
  if (currentProvider.value === 'chatx') return accountsStore.chatxAccounts
  if (currentProvider.value === 'easemate') return accountsStore.easemateAccounts
  return []
})

const openAddModal = () => {
  isEditing.value = false
  if (currentProvider.value === 'chatx') {
    chatxData.id = null
    chatxData.email = ''
    chatxData.password = ''
    chatxData.auto_clear_history = false
  } else {
    easemateData.id = null
    easemateData.device_uuid = ''
    easemateData.identity_id = ''
  }
  showModal.value = true
}

const openEditModal = (acc: any) => {
  isEditing.value = true
  if (currentProvider.value === 'chatx') {
    chatxData.id = acc.id
    chatxData.email = acc.email
    chatxData.password = '' // Don't show password
    chatxData.auto_clear_history = acc.auto_clear_history
  } else {
    easemateData.id = acc.id
    easemateData.device_uuid = acc.device_uuid
    easemateData.identity_id = acc.identity_id
  }
  showModal.value = true
}

const handleSave = async () => {
  submitting.value = true
  let result
  if (currentProvider.value === 'chatx') {
    result = await accountsStore.saveChatXAccount({
      id: chatxData.id,
      email: chatxData.email,
      password: chatxData.password || undefined,
      auto_clear_history: chatxData.auto_clear_history
    })
  } else {
    result = await accountsStore.saveEaseMateAccount({
      id: easemateData.id,
      device_uuid: easemateData.device_uuid,
      identity_id: easemateData.identity_id
    })
  }
  
  if (result?.success) {
    uiStore.showAlert('Đã lưu thông tin tài khoản', 'success')
    showModal.value = false
  } else {
    uiStore.showAlert(result?.message || 'Lưu thất bại', 'error')
  }
  submitting.value = false
}

const handleDelete = async (id: string) => {
  if (confirm('Bạn có chắc chắn muốn xóa tài khoản này?')) {
    const result = await accountsStore.deleteAccount(currentProvider.value as any, id)
    if (result && !result.success) {
      uiStore.showAlert(result.message, 'error')
    } else {
      uiStore.showAlert('Đã xóa tài khoản', 'success')
    }
  }
}

const handleVerify = async () => {
  if (!easemateData.device_uuid || !easemateData.identity_id) return
  verifying.value = true
  const result = await accountsStore.verifyEaseMate(easemateData.device_uuid, easemateData.identity_id)
  if (result.success) {
    uiStore.showAlert('🎉 ' + result.message, 'success')
  } else {
    uiStore.showAlert('❌ ' + result.message, 'error')
  }
  verifying.value = false
}

const toggleInstructions = async () => {
  if (!showInstructions.value) {
    const result = await accountsStore.getEaseMateScript()
    if (result.success) {
      emScript.value = result.script
      showInstructions.value = true
    } else {
      uiStore.showAlert('Không thể tải hướng dẫn', 'error')
    }
  } else {
    showInstructions.value = false
  }
}

const copyScript = () => {
  navigator.clipboard.writeText(emScript.value).then(() => {
    uiStore.showAlert('Đã sao chép script trích xuất', 'success')
  })
}
</script>
