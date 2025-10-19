import { defineStore } from 'pinia'
import { ref, onMounted } from 'vue'
import { useUserStore } from './user.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('auth_user') || null))
  const isAuthenticated = ref(!!localStorage.getItem('auth_token'))
  const loading = ref(false)
  const error = ref(null)
  const showModalAuth = ref(false)
  const userStore = useUserStore()

  // Функция для сохранения авторизации
  function setAuth(userData) {
    user.value = userData
    isAuthenticated.value = true
    userStore.setUser(userData)
    
    // Сохраняем в localStorage
    localStorage.setItem('auth_user', JSON.stringify(userData))
    localStorage.setItem('auth_token', 'authenticated') // или реальный токен если есть
  }

  const allowDeleteAccountUser = () => {
    return ['SU', 'MO']?.includes(user.value?.role)
  }

  // Функция для очистки авторизации
  function clearAuth() {
    user.value = null
    isAuthenticated.value = false
    userStore.clearUser()
    
    // Очищаем localStorage
    localStorage.removeItem('auth_user')
    localStorage.removeItem('auth_token')
  }

  async function login(email, password) {
    loading.value = true
    error.value = null
    try {
      const res = await fetch('/api/accounts/login/', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Ошибка авторизации')
      
      setAuth(data.user) // Используем новую функцию
    } catch (e) {
      error.value = e.message || 'Ошибка сети'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function register(form) {
    loading.value = true
    error.value = null
    try {
      const res = await fetch('/api/accounts/register/', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Ошибка регистрации')
      
      setAuth(data.user) // Используем новую функцию
      showModalAuth.value = false
    } catch (e) {
      error.value = e.message || 'Ошибка сети'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchProfile() {
    loading.value = true
    error.value = null
    try {
      const res = await fetch('/api/accounts/profile/', {
        method: 'GET',
        credentials: 'include'
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Ошибка получения профиля')
      
      setAuth(data) // Используем новую функцию для обновления
    } catch (e) {
      error.value = e.message || 'Ошибка сети'
      clearAuth() // Очищаем при ошибке
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    loading.value = true
    try {
      await fetch('/api/accounts/logout/', {
        method: 'POST',
        credentials: 'include'
      })
    } catch (e) {
      // ignore errors on logout
    } finally {
      clearAuth() // Всегда очищаем локальные данные
      loading.value = false
    }
  }

  // Функция для проверки и восстановления авторизации при загрузке
  async function initializeAuth() {
    if (isAuthenticated.value && user.value) {
      try {
        // Проверяем, что токен/сессия еще валидны
        await fetchProfile()
      } catch (e) {
        // Если профиль не загрузился, очищаем авторизацию
        clearAuth()
      }
    } else {
      // Если в localStorage есть данные, но в store нет - восстанавливаем
      const savedUser = localStorage.getItem('auth_user')
      if (savedUser) {
        user.value = JSON.parse(savedUser)
        isAuthenticated.value = true
        userStore.setUser(user.value)
      }
    }
  }

  return {
    user,
    isAuthenticated,
    loading,
    error,
    showModalAuth,
    login,
    register,
    fetchProfile,
    logout,
    initializeAuth, // Экспортируем функцию инициализации
    setAuth,
    clearAuth,
    allowDeleteAccountUser
  }
})