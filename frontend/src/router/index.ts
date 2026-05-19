import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/DashboardLayout.vue'),
    children: [
      {
        path: 'keys',
        name: 'Keys',
        component: () => import('../views/KeysView.vue')
      },
      {
        path: 'accounts',
        name: 'Accounts',
        component: () => import('../views/AccountsView.vue')
      },
      {
        path: 'test',
        name: 'Test',
        component: () => import('../views/TestView.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory('/admin/'),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('auth_token')
  
  if (to.name !== 'Login' && !token) {
    next({ name: 'Login' })
  } else if (to.name === 'Login' && token) {
    next({ name: 'Keys' })
  } else {
    next()
  }
})

export default router
