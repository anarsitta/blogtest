<template>
  <el-card v-if="post" class="post-view-card">
    <div class="post-title">{{ post.title }}</div>
    <div class="post-description">{{ post.description }}</div>
    <el-tag v-if="post.is_private" type="warning" style="margin-top:6px;">Приватный</el-tag>
    <div class="post-meta">
      <el-text type="info">Автор: {{ post.author?.fullname || post.author?.username }}</el-text>
      <el-text type="info" style="margin-left:12px;">Создан: {{ post.created_at }}</el-text>
    </div>
  </el-card>
  <el-empty v-else description="Пост не найден" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const post = ref(null)

async function fetchPost() {
  try {
    const res = await fetch(`/api/posts/${route.params.id}/`, { credentials: 'include' })
    const data = await res.json()
    if (!res.ok) throw new Error(data.error || 'Ошибка загрузки поста')
    post.value = data.post
  } catch {
    post.value = null
  }
}

onMounted(fetchPost)
</script>

<style scoped>
.post-view-card {
  max-width: 700px;
  margin: 40px auto;
  padding: 32px 24px;
}
.post-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 12px;
}
.post-description {
  font-size: 1.1rem;
  margin-bottom: 18px;
}
.post-meta {
  margin-top: 18px;
}
</style>
