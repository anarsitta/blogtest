<template>
  <el-text :size="'large'" class="title">Профиль пользователя</el-text>
  
  <el-row gutter="32" align="top" style="margin-top: 20px;">
    <el-col :span="16">
      <div class="user-info-block">
        <el-descriptions border column="1" class="profile-descriptions" v-if="user">
          <el-descriptions-item label="Никнейм">{{ user.username }}</el-descriptions-item>
          <el-descriptions-item label="Имя">{{ user.first_name }}</el-descriptions-item>
          <el-descriptions-item label="Фамилия">{{ user.last_name }}</el-descriptions-item>
          <el-descriptions-item label="Email">{{ user.email }}</el-descriptions-item>
          <el-descriptions-item label="Дата регистрации">{{ formatDate(user.date_joined) }}</el-descriptions-item>
          <el-descriptions-item label="Роль">{{ formatRole(user.role) }}</el-descriptions-item>
          <el-descriptions-item label="Последний вход">{{ formatDateTime(user.last_activity) }}</el-descriptions-item>
        </el-descriptions>
        <el-skeleton v-else rows="5" animated />
      </div>
    </el-col>
    
    <el-col :span="8" class="avatar-block">
      <el-avatar :size="120" :src="user?.avatar || defaultAvatar" class="profile-avatar" />
      <el-upload
        class="avatar-uploader"
        action="#"
        :show-file-list="false"
        :auto-upload="false"
      >
        <el-button type="primary" size="small" style="margin-top:12px;">Сменить аватар</el-button>
      </el-upload>
    </el-col>
  </el-row>
  
  <el-row justify="space-between" style="width: 100%; margin-bottom: 18px;">
    <el-button type="primary" @click="showEditModal">Изменить данные</el-button>
    <el-button type="warning" @click="showChangePasswordModal">Сменить пароль</el-button>
    <el-button type="danger" @click="deleteAccount" :loading="deleting">Удалить аккаунт</el-button>
  </el-row>
  
  <el-row justify="space-between" style="width: 100%;">
    <el-text class="post-count" type="info">Всего постов: {{ posts.length }}</el-text>
    <el-button type="primary" @click="goToCreatePost">Создать пост</el-button>
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
        <el-button
          type="danger"
          :icon="Delete"
          circle
          size="small"
          class="delete-post-btn"
          @click.stop="deletePost(post.id)"
        />
      </div>
    </el-card>
    <el-empty v-if="posts.length === 0" description="У вас нет постов" />
  </div>

  <!-- Модальные окна -->
  <EditProfileModal
    :visible="editModalVisible"
    :user="user"
    :loading="saving"
    @update:visible="editModalVisible = $event"
    @save="saveProfile"
  />
  
  <ChangePasswordModal
    :visible="changePasswordModalVisible"
    @update:visible="changePasswordModalVisible = $event"
    @confirm="changePassword"
  />
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '../store/auth.js'
import { useRouter } from 'vue-router'
import { Delete } from '@element-plus/icons-vue'
import { storeToRefs } from 'pinia'
import { useUserStore } from '@/store/user.js'
import EditProfileModal from '../components/EditProfileModal.vue'
import ChangePasswordModal from '../components/ChangePasswordModal.vue'

const authStore = useAuthStore()
const userStore = useUserStore()
const { user } = storeToRefs(authStore)
const router = useRouter()

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
const saving = ref(false)
const deleting = ref(false)
const posts = ref([])

// Состояния модальных окон
const editModalVisible = ref(false)
const changePasswordModalVisible = ref(false)

// Методы для показа модальных окон
const showEditModal = () => {
  editModalVisible.value = true
}

const showChangePasswordModal = () => {
  changePasswordModalVisible.value = true
}

async function loadProfile() {
  await authStore.fetchProfile()
}

async function saveProfile(profileData) {
  saving.value = true
  try {
    await userStore.updateProfile(profileData)
    ElMessage.success('Профиль обновлен')
    editModalVisible.value = false
    await loadProfile()
  } catch (e) {
    ElMessage.error(e.message || 'Ошибка')
  } finally {
    saving.value = false
  }
}

async function deleteAccount() {
  try {
    await ElMessageBox.confirm(
      'Вы уверены, что хотите удалить аккаунт? Это действие необратимо.',
      'Удаление аккаунта',
      { 
        type: 'warning',
        confirmButtonText: 'Удалить',
        cancelButtonText: 'Отмена'
      }
    )
    
    deleting.value = true
    await userStore.deleteAccount()
    ElMessage.success('Аккаунт удален')
    await authStore.logout()
    window.location.href = '/'
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || 'Ошибка удаления аккаунта')
    }
  } finally {
    deleting.value = false
  }
}

async function changePassword(passwordData) {
  try {
    await userStore.changePassword(passwordData)
    ElMessage.success('Пароль успешно изменен')
    changePasswordModalVisible.value = false
  } catch (e) {
    ElMessage.error(e.message || 'Ошибка смены пароля')
  }
}

watch(() => user.value?.id, (id) => {
  if (id) fetchPosts()
})

async function fetchPosts() {
  if (!user.value?.id) {
    posts.value = []
    return
  }
  try {
    posts.value = await userStore.fetchUserPosts(user.value.id)
  } catch (e) {
    posts.value = []
  }
}

function goToCreatePost() {
  router.push('/create-post')
}

function goToPost(id) {
  // router.push(`/post/${id}`)
}

async function deletePost(id) {
  await ElMessageBox.confirm(
    'Вы уверены, что хотите удалить пост? Это действие необратимо.',
    'Удаление поста',
    { 
      type: 'warning',
      confirmButtonText: 'Удалить',
      cancelButtonText: 'Отмена'
    }
  ).then(async () => {
    try {
      await userStore.deleteBlog(id)
      ElMessage.success('Пост удален')
      await fetchPosts()
    } catch (e) {
      ElMessage.error(e.message || 'Ошибка удаления')
    }
  }).catch(() => {})
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

function formatDateTime(dateStr) {
  if (!dateStr) return '—'
  const date = new Date(dateStr)
  return date.toLocaleString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatRole(role) {
  if (!role) return '—'
  const map = {
    admin: 'Администратор',
    US: 'Пользователь',
    moderator: 'Модератор',
    SU: 'Суперпользователь'
  }
  return map[role] || role
}

onMounted(async () => {
  if (!user.value) router.push('/feed')
  await Promise.all([
    loadProfile(),
    fetchPosts()
  ])
})
</script>

<style scoped>
/* Стили остаются без изменений */
.profile-card {
  max-width: 700px;
  margin: 40px auto;
  padding: 32px 24px 24px 24px;
  background: #fff;
}
.profile-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 18px;
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
.avatar-uploader {
  width: 100%;
  text-align: center;
}
.post-count {
  font-size: 1rem;
  font-weight: 500;
  color: #606266;
}
.posts-list {
  margin-top: 18px;
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
.delete-post-btn {
  margin-left: 18px;
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