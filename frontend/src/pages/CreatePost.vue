<template>
  <el-result v-if="!user" icon="warning" title="Внимание"
             sub-title="Для создания поста необходимо авторизоваться."/>
  <div v-else>
    <el-row>
      <el-button type="primary" @click="router.back" :icon="Back" class="back-btn" plain>
        Вернуться назад
      </el-button>
      <el-text :size="'large'" class="title">Создание поста</el-text>
    </el-row>
    <el-text type="info" class="subtitle">
      Для создания поста необходимо заполнить форму и отправить
    </el-text>
    <el-divider/>
    <el-form :model="form" label-position="top">
      <el-form-item label="Название">
        <el-input v-model="form.title" />
      </el-form-item>
      <el-form-item label="Описание">
        <el-input type="textarea" v-model="form.description" rows="5" />
      </el-form-item>
      <el-form-item label="Приватный пост" label-position="left">
        <el-switch v-model="form.is_private" />
      </el-form-item>
      <el-form-item>
        <el-row justify="end" style="width: 100%;">
          <el-button type="primary" @click="createPost" :loading="loading">Создать пост</el-button>
        </el-row>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Back } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const {user} = storeToRefs(authStore)
const router = useRouter()

const form = ref({
  title: '',
  description: '',
  is_private: false
})
const loading = ref(false)

async function createPost() {
  if (!form.value.title || !form.value.description) {
    ElMessage.error('Заполните все поля')
    return
  }
  loading.value = true
  try {
    const res = await fetch('/api/blogs/feed/', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || 'Ошибка создания поста')
    ElMessage.success('Пост создан')
    router.back()
  } catch (e) {
    ElMessage.error(e.message || 'Ошибка')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.title {
  width: auto;
  margin-left: 20px;
}
</style>
