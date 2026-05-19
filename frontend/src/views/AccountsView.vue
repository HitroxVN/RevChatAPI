<template>
  <div class="max-w-5xl mx-auto space-y-12">
    <header class="px-2">
      <h1 class="text-3xl lg:text-5xl font-black text-white tracking-tighter">Tài khoản</h1>
      <p class="text-neutral-500 mt-2 font-bold uppercase tracking-[0.2em] text-[10px] lg:text-xs">Quản lý định danh các nhà cung cấp AI</p>
    </header>

    <!-- Provider Selection -->
    <div v-if="!currentProvider" class="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8">
      <!-- ChatX Provider Card -->
      <div 
        @click="currentProvider = 'chatx'" 
        class="glass-card p-8 lg:p-12 cursor-pointer group hover:bg-white/[0.06] transition-all duration-500 border-white/[0.05] hover:border-yellow-500/30"
      >
        <div class="flex items-center justify-between mb-8 lg:mb-10">
          <div class="p-4 lg:p-5 bg-yellow-500/10 rounded-[24px] lg:rounded-[32px] group-hover:scale-110 transition-transform duration-500">
            <ShieldCheck class="w-10 h-10 lg:w-12 lg:h-12 text-yellow-500" />
          </div>
          <div class="text-neutral-600 group-hover:text-yellow-500 transition-colors">
            <ChevronRight class="w-8 h-8 lg:w-10 lg:h-10" />
          </div>
        </div>
        <h3 class="text-2xl lg:text-3xl font-black text-white tracking-tight">ChatX Provider</h3>
        <p class="text-neutral-500 mt-4 text-sm lg:text-base font-medium leading-relaxed">Quản lý các tài khoản ChatX.</p>
      </div>

      <!-- EaseMate Provider Card -->
      <div 
        @click="currentProvider = 'easemate'" 
        class="glass-card p-8 lg:p-12 cursor-pointer group hover:bg-white/[0.06] transition-all duration-500 border-white/[0.05] hover:border-blue-500/30"
      >
        <div class="flex items-center justify-between mb-8 lg:mb-10">
          <div class="p-4 lg:p-5 bg-blue-500/10 rounded-[24px] lg:rounded-[32px] group-hover:scale-110 transition-transform duration-500">
            <Cpu class="w-10 h-10 lg:w-12 lg:h-12 text-blue-500" />
          </div>
          <div class="text-neutral-600 group-hover:text-blue-500 transition-colors">
            <ChevronRight class="w-8 h-8 lg:w-10 lg:h-10" />
          </div>
        </div>
        <h3 class="text-2xl lg:text-3xl font-black text-white tracking-tight">EaseMate Provider</h3>
        <p class="text-neutral-500 mt-4 text-sm lg:text-base font-medium leading-relaxed">Cấu hình Device UUID và Identity ID cho các model EaseMate.</p>
      </div>
    </div>

    <!-- Account List View -->
    <div v-else class="space-y-8 animate-fade-in">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-6 px-2">
        <div class="flex items-center gap-4 lg:gap-6">
          <button 
            @click="currentProvider = null" 
            class="p-3 lg:p-4 bg-white/[0.03] hover:bg-white/[0.08] text-white rounded-[20px] lg:rounded-[24px] transition-all border border-white/[0.05]"
          >
            <ArrowLeft class="w-5 h-5 lg:w-6 lg:h-6" />
          </button>
          <div>
            <h2 class="text-2xl lg:text-4xl font-black text-white tracking-tight">
              {{ currentProvider === 'chatx' ? 'ChatX Accounts' : 'EaseMate Accounts' }}
            </h2>
            <p class="text-neutral-500 text-[10px] lg:text-xs font-bold uppercase tracking-widest mt-1">
              {{ currentProvider === 'chatx' ? 'Danh sách tài khoản Email/Password' : 'Danh sách Device UUID và Identity ID' }}
            </p>
          </div>
        </div>
        <button 
          @click="openAddModal"
          class="btn-gold px-6 lg:px-8 py-3 lg:py-4 rounded-2xl flex items-center justify-center gap-3 w-full md:w-auto"
        >
          <Plus class="w-5 h-5 lg:w-6 lg:h-6" />
          <span class="text-base lg:text-lg">Thêm Tài khoản</span>
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
          class="glass-card p-6 lg:p-8 group hover:bg-white/[0.06] transition-all duration-500 relative flex flex-col justify-between min-h-[180px]"
          @click="openEditModal(acc)"
        >
          <div>
            <div class="flex items-center justify-between mb-6">
              <div 
                class="p-3 lg:p-4 rounded-2xl group-hover:scale-110 transition-transform duration-500"
                :class="currentProvider === 'chatx' ? 'bg-yellow-500/10' : 'bg-blue-500/10'"
              >
                <ShieldCheck v-if="currentProvider === 'chatx'" class="w-6 h-6 lg:w-8 lg:h-8 text-yellow-500" />
                <Cpu v-else class="w-6 h-6 lg:w-8 lg:h-8 text-blue-500" />
              </div>
              <div class="flex items-center gap-1 lg:gap-2">
                <button 
                  @click.stop="handleDelete(acc.id)"
                  class="p-2 text-neutral-600 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition-all"
                >
                  <Trash2 class="w-4 h-4 lg:w-5 lg:h-5" />
                </button>
                <div class="p-2 text-neutral-600 group-hover:text-white transition-colors">
                  <Edit3 class="w-5 h-5 lg:w-6 lg:h-6" />
                </div>
              </div>
            </div>
            <h3 class="text-xl lg:text-2xl font-black text-white tracking-tight truncate pr-2">
              {{ acc.note || (currentProvider === 'chatx' ? 'ChatX User' : 'EaseMate Device') }}
            </h3>
            <p class="text-[11px] lg:text-sm font-mono text-neutral-500 mt-2 truncate max-w-full opacity-60">
              {{ currentProvider === 'chatx' ? (acc as any).email : (acc as any).device_uuid }}
            </p>
          </div>

          <!-- Account Usage & Verify (EaseMate Only) -->
          <div v-if="currentProvider === 'easemate'" class="mt-6 pt-5 border-t border-white/[0.05] flex items-center justify-between gap-4" @click.stop>
            <div v-if="accountsUsage[acc.id]" class="flex-1 grid grid-cols-1 md:grid-cols-3 gap-3 lg:gap-4">
              <div class="flex flex-col">
                <span class="text-[7px] font-black text-neutral-600 uppercase tracking-wider">Lượt còn lại</span>
                <span class="text-sm font-black text-green-500">{{ accountsUsage[acc.id].remaining_credit }}</span>
              </div>
              <div class="flex flex-col md:border-l md:border-white/[0.05] md:pl-4">
                <span class="text-[7px] font-black text-neutral-600 uppercase tracking-wider">Đã dùng</span>
                <span class="text-[11px] font-bold text-neutral-400">{{ accountsUsage[acc.id].token_spend }}</span>
              </div>
              <div class="flex flex-col md:border-l md:border-white/[0.05] md:pl-4">
                <span class="text-[7px] font-black text-neutral-600 uppercase tracking-wider">Tổng hạn mức</span>
                <span class="text-[11px] font-bold text-neutral-400">{{ accountsUsage[acc.id].token_total }}</span>
              </div>
            </div>
            <div v-else class="flex-1 flex flex-col">
              <span v-if="!acc.is_failed" class="text-[10px] font-bold text-neutral-700 italic">Chưa xác thực</span>
              <span v-else class="px-2 py-0.5 bg-red-500/10 text-red-500 text-[10px] font-black uppercase tracking-widest rounded-md border border-red-500/20 w-fit mt-0.5">Lỗi</span>
            </div>
            
            <button 
              @click="handleVerify(acc)"
              :disabled="verifyingId === acc.id"
              class="px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border shrink-0 h-fit self-end lg:self-center"
              :class="accountsUsage[acc.id] 
                ? 'bg-white/[0.03] text-neutral-400 border-white/[0.05] hover:bg-white/[0.08]' 
                : 'bg-blue-500/10 text-blue-400 border-blue-500/20 hover:bg-blue-500/20'"
            >
              <div class="flex items-center gap-2">
                <Loader2 v-if="verifyingId === acc.id" class="w-3 h-3 animate-spin" />
                <ShieldCheck v-else class="w-3 h-3" />
                <span>{{ accountsUsage[acc.id] ? 'Cập nhật' : 'Xác thực' }}</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 z-[110] flex items-center justify-center modal-backdrop p-2 lg:p-4">
      <div class="w-full max-w-2xl glass-card animate-scale-in flex flex-col h-auto max-h-[90vh] my-auto">
        <!-- Modal Header -->
        <div class="p-5 lg:p-6 border-b border-white/[0.05] flex items-center justify-between shrink-0">
          <div class="flex items-center gap-5">
            <div 
              class="p-3 lg:p-4 rounded-2xl"
              :class="currentProvider === 'chatx' ? 'bg-yellow-500/10' : 'bg-blue-500/10'"
            >
              <ShieldCheck v-if="currentProvider === 'chatx'" class="w-6 h-6 lg:w-8 lg:h-8 text-yellow-500" />
              <Cpu v-else class="w-6 h-6 lg:w-8 lg:h-8 text-blue-500" />
            </div>
            <div>
              <h3 class="text-xl lg:text-2xl font-black text-white tracking-tight">
                {{ isEditing ? 'Cập nhật' : 'Thêm mới' }} {{ currentProvider === 'chatx' ? 'ChatX' : 'EaseMate' }}
              </h3>
              <p class="text-[9px] lg:text-[10px] text-neutral-500 font-bold uppercase tracking-widest mt-1">Cấu hình thông tin nhà cung cấp</p>
            </div>
          </div>
          <button @click="showModal = false" class="text-neutral-500 hover:text-white transition-transform hover:rotate-90">
            <X class="w-8 h-8 lg:w-10 lg:h-10" />
          </button>
        </div>

        <!-- Scrollable Content -->
        <div class="overflow-y-auto flex-1 custom-scrollbar">
          <!-- ChatX Fields -->
          <div v-if="currentProvider === 'chatx'" class="p-6 lg:p-8 space-y-6 lg:space-y-8">
            <div class="space-y-3">
              <label class="block text-[10px] font-black text-neutral-500 ml-1 uppercase tracking-[0.2em]">Ghi chú tài khoản</label>
              <input v-model="chatxData.note" type="text" class="w-full glass-input p-4 lg:p-5" placeholder="Ví dụ: Tài khoản chính, Free 1, ...">
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8">
              <div class="space-y-3">
                <label class="block text-[10px] font-black text-neutral-500 ml-1 uppercase tracking-[0.2em]">Địa chỉ Email</label>
                <input v-model="chatxData.email" type="email" class="w-full glass-input p-4 lg:p-5" placeholder="user@example.com">
              </div>
              <div class="space-y-3">
                <label class="block text-[10px] font-black text-neutral-500 ml-1 uppercase tracking-[0.2em]">Mật khẩu mới</label>
                <input v-model="chatxData.password" type="password" class="w-full glass-input p-4 lg:p-5" placeholder="••••••••">
              </div>
            </div>
            <div class="flex items-center justify-between p-5 lg:p-6 bg-white/[0.03] rounded-[24px] lg:rounded-[32px] border border-white/[0.05]">
              <div>
                <div class="text-base lg:text-lg font-black text-white tracking-tight">Tự động xóa lịch sử</div>
                <div class="text-[10px] lg:text-xs text-neutral-500 font-medium mt-1">Làm sạch context AI sau mỗi request</div>
              </div>
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="chatxData.auto_clear_history" class="sr-only peer">
                <div class="w-14 h-7 lg:w-16 lg:h-8 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[4px] after:left-[4px] after:bg-white after:rounded-full after:h-5 after:w-5 lg:after:h-6 lg:after:w-6 after:transition-all peer-checked:bg-yellow-500 shadow-inner"></div>
              </label>
            </div>
          </div>

          <!-- EaseMate Fields -->
          <div v-if="currentProvider === 'easemate'" class="p-6 lg:p-8 space-y-6">
            <div class="flex justify-between items-center bg-blue-500/10 p-4 lg:p-5 rounded-[20px] lg:rounded-[28px] border border-blue-500/20">
              <div class="flex items-center gap-3 text-blue-400">
                <Info class="w-5 h-5 lg:w-6 lg:h-6" />
                <span class="text-[9px] lg:text-xs font-black uppercase tracking-widest">Dán cấu hình JSON từ Console</span>
              </div>
              <button @click="toggleInstructions" class="px-4 lg:px-5 py-2 lg:py-2.5 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 text-[9px] lg:text-[10px] font-black uppercase tracking-widest rounded-xl transition-all border border-blue-500/20">
                {{ showInstructions ? 'Đóng' : 'Xem hướng dẫn' }}
              </button>
            </div>

            <transition name="fade">
              <div v-if="showInstructions" class="p-5 lg:p-6 bg-black/60 rounded-[24px] lg:rounded-[32px] border border-white/[0.05] space-y-4">
                <div class="text-[11px] lg:text-xs text-neutral-400 space-y-2 leading-relaxed">
                  <p>1. Gửi tin nhắn tại: <a href="https://www.easemate.ai" target="_blank" class="text-blue-400 hover:underline">easemate.ai</a></p>
                  <p>2. Mở Console (F12) &rarr; Dán Script &rarr; Enter</p>
                  <p>3. Dán kết quả JSON vào ô bên dưới</p>
                </div>
                <div class="pt-4 border-t border-white/[0.05] flex items-center justify-between">
                  <span class="text-[9px] lg:text-[10px] font-black text-blue-500 uppercase tracking-[0.2em]">JS Extraction Script</span>
                  <button @click="copyScript" class="flex items-center gap-2 text-[9px] lg:text-[10px] font-black text-neutral-400 hover:text-white bg-white/5 px-3 py-1.5 lg:px-4 lg:py-2 rounded-xl transition-all">
                    <Copy class="w-3.5 h-3.5 lg:w-4 lg:h-4" />
                    <span>SAO CHÉP</span>
                  </button>
                </div>
                <pre class="p-4 bg-black/40 rounded-2xl border border-white/[0.03] text-[9px] lg:text-[10px] font-mono text-blue-300/50 overflow-x-auto max-h-32 custom-scrollbar">{{ emScript }}</pre>
              </div>
            </transition>

            <div class="space-y-3">
              <label class="block text-[10px] font-black text-neutral-500 ml-1 uppercase tracking-[0.2em]">Ghi chú tài khoản</label>
              <input v-model="easemateData.note" type="text" class="w-full glass-input p-4 lg:p-5" placeholder="Ví dụ: Tài khoản chính, Guest 1, ...">
            </div>

            <div class="space-y-3">
              <label class="block text-[10px] font-black text-neutral-500 ml-1 uppercase tracking-[0.2em]">Cấu hình JSON (Pasted from Console)</label>
              <textarea 
                v-model="easemateData.json_input" 
                class="w-full glass-input p-4 lg:p-5 font-mono text-[11px] lg:text-xs min-h-[120px] lg:min-h-[150px] resize-none custom-scrollbar" 
                placeholder='{ "device_uuid": "...", "identity_id": "...", "token": "..." }'
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="p-5 lg:p-6 border-t border-white/[0.05] flex justify-end gap-3 lg:gap-4 shrink-0 bg-black/20">
          <button @click="showModal = false" class="px-5 lg:px-6 py-2.5 lg:py-3 rounded-xl bg-white/[0.03] text-white hover:bg-white/[0.08] font-bold transition-all text-sm">Hủy</button>
          <button @click="handleSave" :disabled="submitting" class="btn-gold px-6 lg:px-10 py-2.5 lg:py-3 rounded-xl flex items-center gap-2">
            <Loader2 v-if="submitting" class="w-5 h-5 animate-spin" />
            <Save v-else class="w-5 h-5" />
            <span class="text-base font-black">Lưu lại</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive, watch } from 'vue'
import { 
  ShieldCheck, Cpu, ChevronRight, ArrowLeft, Plus, 
  Loader2, FolderOpen, Trash2, Edit3, X, Info, Copy, Save
} from 'lucide-vue-next'
import { useAccountsStore } from '@/stores/accountsStore'
import { useUIStore } from '@/stores/uiStore'

const accountsStore = useAccountsStore()
const uiStore = useUIStore()
const currentProvider = ref<'chatx' | 'easemate' | null>(null)
const isEditing = ref(false)
const showModal = ref(false)
const submitting = ref(false)
const verifyingId = ref<string | null>(null)
const showInstructions = ref(false)
const emScript = ref('')
const accountsUsage = reactive<Record<string, any>>({})

const chatxData = reactive({
  id: null as string | null,
  email: '',
  password: '',
  auto_clear_history: false,
  note: ''
})

const easemateData = reactive({
  id: null as string | null,
  device_uuid: '',
  identity_id: '',
  token: '',
  json_input: '',
  note: ''
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
    chatxData.note = ''
  } else {
    easemateData.id = null
    easemateData.device_uuid = ''
    easemateData.identity_id = ''
    easemateData.token = ''
    easemateData.json_input = ''
    easemateData.note = ''
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
    chatxData.note = acc.note || ''
  } else {
    easemateData.id = acc.id
    easemateData.device_uuid = acc.device_uuid
    easemateData.identity_id = acc.identity_id
    easemateData.token = acc.token || ''
    easemateData.note = acc.note || ''
    easemateData.json_input = JSON.stringify({
      device_uuid: acc.device_uuid,
      identity_id: acc.identity_id,
      token: acc.token || ''
    }, null, 4)
  }
  showModal.value = true
}

// Tự động parse JSON khi người dùng dán vào
watch(() => easemateData.json_input, (val) => {
  if (!val) return
  try {
    const data = JSON.parse(val)
    if (data.device_uuid) easemateData.device_uuid = data.device_uuid
    if (data.identity_id) easemateData.identity_id = data.identity_id
    if (data.token) easemateData.token = data.token
  } catch (e) {
    // Không phải JSON hợp lệ, bỏ qua
  }
})

const handleSave = async () => {
  submitting.value = true
  let result
  if (currentProvider.value === 'chatx') {
    result = await accountsStore.saveChatXAccount({
      id: chatxData.id,
      email: chatxData.email,
      password: chatxData.password || undefined,
      auto_clear_history: chatxData.auto_clear_history,
      note: chatxData.note
    })
  } else {
    result = await accountsStore.saveEaseMateAccount({
      id: easemateData.id,
      device_uuid: easemateData.device_uuid,
      identity_id: easemateData.identity_id,
      token: easemateData.token,
      note: easemateData.note
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

const handleVerify = async (acc: any) => {
  if (currentProvider.value !== 'easemate') return
  verifyingId.value = acc.id
  const result = await accountsStore.verifyEaseMate(acc.device_uuid, acc.identity_id, acc.token)
  if (result.success) {
    uiStore.showAlert('🎉 ' + result.message, 'success')
    if (result.usage) {
      accountsUsage[acc.id] = result.usage
    }
  } else {
    uiStore.showAlert('❌ ' + result.message, 'error')
    delete accountsUsage[acc.id]
  }
  
  await accountsStore.loadAllAccounts()
  verifyingId.value = null
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
