<template>
  <div class="min-h-screen flex bg-[#050505] relative overflow-hidden">
    <!-- Vibrant Background Blobs -->
    <div class="vibrant-blob w-[500px] h-[500px] bg-blue-600/20 -top-48 -left-24"></div>
    <div class="vibrant-blob w-[600px] h-[600px] bg-purple-600/10 top-1/2 -right-48"></div>
    <div class="vibrant-blob w-[400px] h-[400px] bg-yellow-500/10 -bottom-24 left-1/3"></div>

    <!-- Sidebar -->
    <aside class="w-80 glass-sidebar p-8 fixed h-full overflow-y-auto z-50 flex flex-col">
      <div class="flex items-center gap-4 mb-14 px-2">
        <div class="relative group">
          <div class="absolute -inset-2 bg-yellow-500/20 rounded-[22px] blur-xl group-hover:bg-yellow-500/30 transition-all duration-700 opacity-50"></div>
          <div class="relative w-14 h-14 bg-white rounded-2xl overflow-hidden shadow-2xl border border-white/10 flex items-center justify-center p-1.5 transform group-hover:scale-105 transition-transform duration-500">
            <img src="/logo.png" alt="Logo" class="w-full h-full object-contain" />
          </div>
        </div>
        <div class="flex flex-col justify-center">
          <h1 class="text-2xl font-black tracking-tighter text-white leading-tight">RevChatAPI</h1>
          <div class="flex items-center gap-1.5">
            <div class="w-1.5 h-1.5 rounded-full bg-yellow-500 animate-pulse"></div>
            <p class="text-[10px] text-neutral-500 font-black uppercase tracking-[0.2em]">Dashboard</p>
          </div>
        </div>
      </div>

      <nav class="space-y-2.5 flex-1">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-4 px-5 py-4 rounded-2xl transition-all duration-500 font-bold group relative overflow-hidden"
          :class="$route.path === item.path ? 'text-white glass-card border-white/10' : 'text-neutral-500 hover:text-neutral-300 hover:bg-white/[0.03]'"
        >
          <!-- Active Glow Effect -->
          <div v-if="$route.path === item.path" class="absolute inset-0 bg-gradient-to-r from-yellow-500/10 to-transparent"></div>
          <div v-if="$route.path === item.path" class="absolute left-0 top-3 bottom-3 w-1 bg-yellow-500 rounded-full shadow-[0_0_15px_rgba(251,191,36,0.8)]"></div>
          
          <component :is="item.icon" class="w-5 h-5 transition-all duration-500 group-hover:scale-110" :class="$route.path === item.path ? 'text-yellow-500' : 'text-neutral-500'" />
          <span class="tracking-tight text-[15px]">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="mt-auto pt-8">
        <button 
          @click="handleLogout"
          class="flex items-center gap-4 px-6 py-4 rounded-2xl text-neutral-500 hover:text-red-400 hover:bg-red-500/[0.05] transition-all duration-500 w-full font-bold group border border-transparent hover:border-red-500/10"
        >
          <LogOut class="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
          <span class="tracking-tight text-[15px]">Đăng xuất</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 ml-80 p-12 min-h-screen relative z-10">
      <router-view v-slot="{ Component }">
        <transition name="fade-slide" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { Zap, Key, UserCircle, MessageSquare, LogOut } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const menuItems = [
  { path: '/keys', label: 'API Keys', icon: Key },
  { path: '/accounts', label: 'Tài khoản', icon: UserCircle },
  { path: '/test', label: 'Test API', icon: MessageSquare },
]

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
