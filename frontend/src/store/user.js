import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)

  function setUser(userData) {
    user.value = userData
  }

  function clearUser() {
    user.value = null
  }

  async function fetchProfile() {
    const res = await fetch('/api/accounts/profile/', {
      method: 'GET',
      credentials: 'include'
    })
    if (!res.ok) throw new Error('Ошибка получения профиля')
    user.value = await res.json()
    return user.value
  }

  async function fetchAuthorProfile(username) {
    const res = await fetch(`/api/accounts/profile/${username}/`)
    if (!res.ok) throw new Error('Ошибка получения профиля автора')
    return await res.json()
  }

  async function updateProfile(payload) {
      const res = await fetch('/api/accounts/profile/', {
        method: 'PUT',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Ошибка обновления профиля')
      return data
    }

    async function deleteAccount() {
      const res = await fetch('/api/accounts/account/', {
        method: 'POST',
        credentials: 'include'
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Ошибка удаления аккаунта')
      return data
    }

    async function deleteAccountById(idUser) {
      const res = await fetch(`/api/accounts/moderator/delete-user/${idUser}/`, {
        method: 'POST',
        credentials: 'include'
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Ошибка удаления аккаунта')
      return data
    }

    async function changePassword(payload) {
      const res = await fetch('/api/accounts/change-password/', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      let data
      try {
        data = await res.json()
      } catch {
        throw new Error('Ошибка смены пароля')
      }
      if (!res.ok) {
        console.error('Ошибка смены пароля:', data)
        throw new Error(data.error || 'Ошибка смены пароля')
      }
      return data
    }
    
    async function fetchUserPosts(userId) {
      const res = await fetch(`/api/blogs/user/id/${userId}/blogs/`, 
        { method: 'GET',  credentials: 'include',
        headers: { 'Content-Type': 'application/json' }, })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Ошибка загрузки постов')
      return data.results || []
    }

    async function deleteBlog(blogId) {
      const res = await fetch('/api/blogs/feed/', {
        method: 'DELETE',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ blog_id: blogId })
      })
      if (!res.ok) {
        let data
        try { data = await res.json() } catch {}
        throw new Error((data && data.error) || 'Ошибка удаления поста')
      }
      return true
    }

  return {
    user, 
    setUser, 
    clearUser,
    fetchProfile,
    fetchAuthorProfile,
    updateProfile,
    deleteAccount,
    changePassword,
    fetchUserPosts,
    deleteBlog,
    deleteAccountById,
  }
})
