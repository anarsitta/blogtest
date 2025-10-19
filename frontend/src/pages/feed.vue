<template>
  <el-row style="width: 100%;" justify="space-between">
    <el-text :size="'large'" class="title">Лента блогов</el-text>
    <el-button v-if="!!user" type="primary" @click="router.push('/create-post')">Создать пост</el-button>
  </el-row>
  
  <el-row :gutter="16">
    <el-col :span="24">
      <el-card 
        v-for="blog in blogs" 
        :key="blog.id" 
        class="blog-card"
        shadow="hover"
      >
        <div class="blog-content">
          <div class="blog-header">
            <div class="blog-header-content">
              <span class="blog-title">{{ blog.title }}</span>
              <el-tag v-if="blog.is_private" type="danger" size="small">Приватный</el-tag>
            </div>
          </div>
          
          <div class="blog-description">{{ blog.description }}</div>
          
          <div class="blog-footer">
            <div class="blog-meta">
              <el-text type="info" class="author-info">
                Автор:
                <router-link
                  :to="`/profile/${blog.author_username}`"
                  class="author-link"
                >
                  {{ blog.author_username }}
                </router-link>
              </el-text>
              <el-text type="info" class="blog-date" v-if="blog.created_at">
                {{ formatDate(blog.created_at) }}
              </el-text>
            </div>
            
            <el-button
              v-if="showBtnDeletePost(blog)"
              type="danger"
              :icon="Delete"
              class="delete-post-btn"
              @click.stop="deletePost(blog.id)"
            >
              Удалить
            </el-button>
          </div>
        </div>
      </el-card>
      
      <el-empty v-if="blogs.length === 0" description="Нет блогов для отображения" />
      
      <el-pagination
        v-if="numPages > 1"
        :current-page="page"
        :page-size="20"
        :total="count"
        layout="prev, pager, next"
        @current-change="handlePageChange"
        class="pagination"
      />
    </el-col>
  </el-row>
</template>

<script setup>
import { useAuthStore } from '@/store/auth'
import { storeToRefs } from 'pinia'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Delete } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const blogs = ref([])
const page = ref(1)
const count = ref(0)
const numPages = ref(1)
const router = useRouter()
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)
const userStore = useUserStore()

async function fetchFeed(pageNumber = 1) {
  const res = await fetch(`/api/blogs/feed/?page=${pageNumber}`)
  const data = await res.json()
  blogs.value = data.results
  count.value = data.count
  numPages.value = data.num_pages
  page.value = data.page
}

function handlePageChange(newPage) {
  fetchFeed(newPage)
}

function showBtnDeletePost(blog) {
  return blog.author === user.value?.id || ['SU', 'MO']?.includes(user.value?.role)
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
      await fetchFeed(page.value)
    } catch (e) {
      ElMessage.error(e.message || 'Ошибка удаления')
    }
  }).catch(() => {})
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(() => {
  fetchFeed()
})
</script>

<style scoped>
.title {
  width: auto;
  margin-bottom: 24px;
}

.blog-card {
  margin: 16px 0;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
  position: relative;
}

.blog-card:hover {
  box-shadow: 0 4px 18px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.blog-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.blog-header-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.blog-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #1f2d3d;
  margin: 0;
  line-height: 1.4;
}

.blog-description {
  margin-bottom: 16px;
  font-size: 15px;
  line-height: 1.6;
  color: #5a5a5a;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.blog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f5f5f5;
}

.blog-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.author-info {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.author-link {
  color: #409EFF;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.author-link:hover {
  color: #1867c0;
  text-decoration: underline;
}

.blog-date {
  font-size: 13px;
  color: #8c8c8c;
}

.delete-post-btn {
  opacity: 0.8;
  transition: all 0.2s ease;
  margin-left: auto;
}

.delete-post-btn:hover {
  opacity: 1;
  transform: scale(1.05);
}

.pagination {
  margin-top: 32px;
  justify-content: center;
}

/* Адаптивность */
@media (max-width: 768px) { 
  .blog-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .blog-header-content {
    width: 100%;
  }
  
  .blog-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .blog-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    width: 100%;
  }
  
  .delete-post-btn {
    margin-left: 0;
    align-self: flex-end;
  }
  
  .blog-title {
    font-size: 1.1rem;
  }
}

/* Анимация появления карточек */
.blog-card {
  animation: fadeInUp 0.5s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Стили для пустого состояния */
:deep(.el-empty__description) {
  margin-top: 16px;
  color: #8c8c8c;
}
:deep(.el-card__body) {
  padding: 14px;
}
</style>