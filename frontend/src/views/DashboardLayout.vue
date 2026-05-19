<template>
  <div class="min-h-screen bg-[#050505] relative overflow-x-hidden">
    <div class="lg:hidden fixed top-0 left-0 right-0 h-16 glass-sidebar flex items-center justify-between px-6 z-[60] border-b border-white/5">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 bg-white/10 rounded-lg flex items-center justify-center p-1 border border-white/10">
          <img src="/logo.png" alt="Logo" class="w-full h-full object-contain" />
        </div>
        <span class="text-lg font-black tracking-tighter text-white">RevChatAPI</span>
      </div>
      <button @click="isSidebarOpen = !isSidebarOpen" class="p-2 text-neutral-400 hover:text-white transition-all active:scale-90">
        <Menu v-if="!isSidebarOpen" class="w-6 h-6" />
        <X v-else class="w-6 h-6" />
      </button>
    </div>

    <!-- Sidebar Backdrop -->
    <transition name="fade">
      <div 
        v-if="isSidebarOpen" 
        @click="isSidebarOpen = false"
        class="lg:hidden fixed inset-0 bg-black/80 backdrop-blur-md z-[45]"
      ></div>
    </transition>

    <!-- Vibrant Background Blobs -->
    <div class="vibrant-blob w-[300px] md:w-[500px] h-[300px] md:h-[500px] bg-blue-600/20 -top-24 md:-top-48 -left-12 md:-left-24"></div>
    <div class="vibrant-blob w-[400px] md:w-[600px] h-[400px] md:h-[600px] bg-purple-600/10 top-1/2 -right-24 md:-right-48"></div>
    <div class="vibrant-blob w-[250px] md:w-[400px] h-[250px] md:h-[400px] bg-yellow-500/10 -bottom-12 md:-bottom-24 left-1/4 md:left-1/3"></div>

    <!-- Sidebar -->
    <aside 
      class="w-72 md:w-80 glass-sidebar p-6 md:p-8 fixed top-0 left-0 bottom-0 h-full overflow-y-auto z-50 flex flex-col transition-all duration-500 ease-in-out lg:translate-x-0 shadow-2xl"
      :class="isSidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="flex items-center gap-4 mb-12 md:mb-14 px-2">
        <div class="relative group">
          <div class="absolute -inset-2 bg-yellow-500/20 rounded-[22px] blur-xl group-hover:bg-yellow-500/30 transition-all duration-700 opacity-50"></div>
          <div class="relative w-12 h-12 md:w-14 md:h-14 bg-white rounded-2xl overflow-hidden shadow-2xl border border-white/10 flex items-center justify-center p-1.5 transform group-hover:scale-105 transition-transform duration-500">
            <img src="/logo.png" alt="Logo" class="w-full h-full object-contain" />
          </div>
        </div>
        <div class="flex flex-col justify-center">
          <h1 class="text-xl md:text-2xl font-black tracking-tighter text-white leading-tight">RevChatAPI</h1>
          <div class="flex items-center gap-1.5">
            <div class="w-1.5 h-1.5 rounded-full bg-yellow-500 animate-pulse"></div>
            <p class="text-[9px] md:text-[10px] text-neutral-500 font-black uppercase tracking-[0.2em]">Dashboard</p>
          </div>
        </div>
      </div>

      <nav class="space-y-2 flex-1">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path"
          :to="item.path"
          @click="isSidebarOpen = false"
          class="flex items-center gap-3.5 md:gap-4 px-4 md:px-5 py-3.5 md:py-4 rounded-xl md:rounded-2xl transition-all duration-500 font-bold group relative overflow-hidden"
          :class="$route.path === item.path ? 'text-white glass shadow-lg border-white/10' : 'text-neutral-500 hover:text-neutral-300 hover:bg-white/[0.03]'"
        >
          <!-- Active Glow Effect -->
          <div v-if="$route.path === item.path" class="absolute inset-0 bg-gradient-to-r from-yellow-500/10 to-transparent"></div>
          <div v-if="$route.path === item.path" class="absolute left-0 top-3 bottom-3 w-1 bg-yellow-500 rounded-full shadow-[0_0_15px_rgba(251,191,36,0.8)]"></div>
          
          <component :is="item.icon" class="w-5 h-5 transition-all duration-500 group-hover:scale-110" :class="$route.path === item.path ? 'text-yellow-500' : 'text-neutral-500'" />
          <span class="tracking-tight text-sm md:text-[15px]">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="mt-auto pt-6">
        <button 
          @click="handleLogout"
          class="flex items-center gap-4 px-6 py-4 rounded-2xl text-neutral-500 hover:text-red-400 hover:bg-red-500/[0.05] transition-all duration-500 w-full font-bold group border border-transparent hover:border-red-500/10"
        >
          <LogOut class="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
          <span class="tracking-tight text-sm md:text-[15px]">Đăng xuất</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main 
      class="min-h-screen transition-all duration-500 ease-in-out relative z-10"
      :class="[
        'lg:ml-72 xl:ml-80',
        'p-4 md:p-8 lg:p-12',
        'pt-24 lg:pt-12'
      ]"
    >
      <div class="max-w-7xl mx-auto">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Zap, Key, UserCircle, MessageSquare, LogOut, Menu, X } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()
const isSidebarOpen = ref(false)

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
