<template>
  <el-row>
    <el-button type="primary" @click="goBack" :icon="ArrowLeft" class="back-btn" plain>
      Назад к ленте
    </el-button>
    <el-text :size="'large'" class="title title-profile">Профиль пользователя</el-text>
  </el-row>
  
  <el-row gutter="32" align="top" v-if="!authRequired" style="margin-top: 20px;">
    <el-col :span="16">
      <div class="user-info-block">
        <el-descriptions border column="1" class="profile-descriptions" v-if="user">
          <el-descriptions-item label="Никнейм">{{ user.username }}</el-descriptions-item>
          <el-descriptions-item label="ФИО">{{ user.fullname }}</el-descriptions-item>
          <el-descriptions-item label="Email">{{ user.email }}</el-descriptions-item>
          <el-descriptions-item label="Дата регистрации">{{ user.date_joined }}</el-descriptions-item>
          <el-descriptions-item label="Роль">{{ formatRole(user.role) }}</el-descriptions-item>
          <el-descriptions-item label="Последний вход">{{ user.last_login || '—' }}</el-descriptions-item>
        </el-descriptions>
        <el-skeleton v-else rows="6" animated />
      </div>
    </el-col>
    <el-col :span="8" class="avatar-block">
      <el-avatar :size="120" :src="user?.avatar || defaultAvatar" class="profile-avatar" />
    </el-col>
  </el-row>
  <el-row v-if="user" class="author-actions" justify="space-between" style="width: 100%;">
    <el-row>
      <el-button type="success" :disabled="inWhitelist" @click="addToList('whitelist')" style="margin-right: 10px;">
        Добавить в белый список
      </el-button>
      <el-button type="danger" :disabled="inBlacklist" @click="addToList('blacklist')">
        Добавить в черный список
      </el-button>
    </el-row>
    <el-button type="danger" v-if="allowDeleteAccountUser" plain @click="deleteAccountById(user.id)">
      Удалить аккаунт
    </el-button>
  </el-row>
  <el-result v-if="authRequired" icon="warning" title="Внимание"
             sub-title="Для просмотра профиля пользователя необходимо авторизоваться или зарегистрироваться.">
  </el-result>
  
  <el-divider />
  <div class="profile-footer" v-if="!authRequired">
    <el-text type="info" class="list-status">
      {{
        inWhitelist
          ? 'Пользователь находится в вашем белом списке'
          : inBlacklist
            ? 'Пользователь находится в вашем черном списке'
            : 'Пользователь не находится в ваших списках'
      }}
    </el-text>
  </div>

  <!-- Секция с постами автора -->
  <div v-if="!authRequired && user" class="author-posts-section">
    <el-row justify="space-between" style="width: 100%; margin: 24px 0 18px 0;">
      <el-text class="post-count" type="info">Всего постов: {{ posts.length }}</el-text>
    </el-row>
    
    <div class="posts-list">
      <el-card
        v-for="post in posts"
        :key="post.id"
        class="feed-post-card"
        shadow="never"
      >
        <div class="feed-post-content">
          <div class="feed-post-main" @click="goToPost(post.id)">
            <div class="post-title">{{ post.title }}</div>
            <div class="post-description">{{ post.description }}</div>
            <el-tag v-if="post.is_private" type="warning" style="margin-top:6px;">Приватный</el-tag>
          </div>
        </div>
      </el-card>
      <el-empty v-if="posts.length === 0" description="У пользователя нет постов" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { useUserStore } from '../store/user.js'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth.js'
import { storeToRefs } from 'pinia'

const route = useRoute()
const router = useRouter()
const user = ref(null)
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
const authRequired = ref(false)
const userStore = useUserStore()
const authStore = useAuthStore()
const {allowDeleteAccountUser} = storeToRefs(authStore)
const posts = ref([])

const inWhitelist = ref(false)
const inBlacklist = ref(false)

async function checkLists(username) {
  try {
    const res = await fetch('/api/accounts/lists/', { credentials: 'include' })
    if (!res.ok) return
    const data = await res.json()
    inWhitelist.value = (data.whitelist || []).some(u => u.username === username)
    inBlacklist.value = (data.blacklist || []).some(u => u.username === username)
  } catch {
    inWhitelist.value = false
    inBlacklist.value = false
  }
}

async function addToList(listType) {
  try {
    const res = await fetch(`/api/accounts/lists/${listType}/${user.value.id}/`, {
      method: 'POST',
      credentials: 'include'
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || 'Ошибка')
    ElMessage.success(data.message || 'Успешно')
    await checkLists(user.value.username)
  } catch (e) {
    ElMessage.error(e.message || 'Ошибка')
  }
}

// Загрузка постов автора
async function fetchAuthorPosts(userId) {
  if (!userId) {
    posts.value = []
    return
  }
  try {
    posts.value = await userStore.fetchUserPosts(userId)
  } catch (e) {
    posts.value = []
    ElMessage.error('Не удалось загрузить посты автора')
  }
}

function goToPost(id) {
  router.push(`/post/${id}`)
}

onMounted(() => {
  loadAuthorProfile(route.params.username)
})

// Следим за изменением пользователя и загружаем его посты
watch(() => user.value, (newUser) => {
  if (newUser && newUser.id) {
    fetchAuthorPosts(newUser.id)
  }
})

function formatRole(role) {
  if (!role) return '—'
  const map = {
    admin: 'Администратор',
    US: 'Пользователь',
    MO: 'Модератор',
    SU: 'Суперпользователь'
  }
  return map[role] || role
}

async function deleteAccountById(idUser) {    
  await ElMessageBox.confirm(
    'Вы уверены, что хотите удалить аккаунт? Это действие необратимо.',
    'Удаление аккаунта',
    { 
      type: 'warning',
      confirmButtonText: 'Удалить',
      cancelButtonText: 'Отмена'
    }
  ).then(async x => {
    try {
      await userStore.deleteAccountById(idUser)
      ElMessage.success('Аккаунт удален')
      router.back()
    } catch (e) {
      ElMessage.error(e.message || 'Ошибка удаления аккаунта')
    } finally {
      deleting.value = false
    }
  }).catch()
}


async function loadAuthorProfile(username) {
  try {
    await userStore.fetchProfile()
    const currentUser = userStore.user
    if (currentUser && currentUser.username === username) {
      router.replace('/profile')
      return
    }
    user.value = await userStore.fetchAuthorProfile(username)
    await checkLists(username)
  } catch (e) {
    authRequired.value = true
    user.value = null
  }
}

function goBack() {
  router.push('/feed')
}
</script>

<style scoped>
.title {
  font-weight: 500;
  font-size: 20px !important;
  width: 100%;
}
.user-info-block {
  margin-bottom: 12px;
}
.profile-descriptions {
  margin-bottom: 8px;
}
.avatar-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
}
.profile-avatar {
  margin-bottom: 8px;
  box-shadow: 0 2px 12px #409eff22;
}
.profile-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 32px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}
.auth-alert {
  margin: 32px 0;
}
.author-actions {
  margin-bottom: 18px;
}
.title-profile {
  width: auto;
  margin: 0 16px;
}

/* Стили для секции постов */
.author-posts-section {
  margin-top: 32px;
}
.post-count {
  font-size: 1rem;
  font-weight: 500;
  color: #606266;
}
.posts-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.feed-post-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px #409eff11;
  padding: 0;
}
.feed-post-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px;
}
.feed-post-main {
  flex: 1;
  cursor: pointer;
}
.post-title {
  font-weight: bold;
  font-size: 1.1rem;
  margin-bottom: 6px;
}
.post-description {
  font-size: 1rem;
  color: #333;
}
:deep(.el-card__body) {
  padding: 0;
}
</style>