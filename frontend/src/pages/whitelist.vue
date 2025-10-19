<template>
    <el-result v-if="authRequired" icon="warning" title="Внимание"
             sub-title="Для просмотра белого списка необходимо авторизоваться."/>
    <div v-else>
        <el-text :size="'large'" class="title">Ваш белый список</el-text>
        <el-text type="info" class="subtitle">
            Это пользователи, для которых будут видны ваши приватные посты.
        </el-text>
    
        <div class="blacklist-list">
            <el-card v-for="user in users" :key="user.id" class="blacklist-card" shadow="never">
                <div class="card-content">
                    <el-icon class="user-icon"><User/></el-icon>
                    <div class="user-info">
                        <el-row>
                            <div class="fullname">{{ user.fullname }}</div>
                            <el-tag type="primary">{{ user.username }}</el-tag>
                            <el-tag type="info">{{ user.email }}</el-tag>
                        </el-row>
                    </div>
                    <el-button type="danger" size="small" :icon="Delete" @click="removeUser(user.id)">Удалить</el-button>
                </div>
            </el-card>
            <el-empty v-if="users.length === 0" description="Список пуст" />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElIcon, ElMessage } from 'element-plus'
import { Delete, User } from '@element-plus/icons-vue'

const users = ref([])
const authRequired = ref(false)

async function fetchWhitelist() {
    try {
        const res = await fetch('/api/accounts/lists/', { credentials: 'include' })
        if ([401, 403]?.includes(res.status)) {
            authRequired.value = true
            users.value = []
            return
        }
        const data = await res.json()
        users.value = data.whitelist || []
    } catch {
        authRequired.value = true
        users.value = []
    }
}

async function removeUser(id) {
    try {
        const res = await fetch(`/api/accounts/lists/whitelist/${id}/`, {
            method: 'DELETE',
            credentials: 'include'
        })
        const data = await res.json()
        if (!res.ok) throw new Error(data.error || 'Ошибка удаления')
        users.value = users.value.filter(u => u.id !== id)
        ElMessage({
            message: data.message || 'Пользователь удален из приватного списка',
            type: 'success',
        })
    } catch (e) {
        ElMessage({
            message: e.message || 'Ошибка удаления',
            type: 'error',
        })
    }
}

onMounted(() => {
    fetchWhitelist()
})
</script>

<style scoped>
.blacklist-list {
    margin-top: 24px;
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.blacklist-card {
    padding: 0;
    border-radius: 10px;
    box-shadow: 0 2px 8px #409eff11;
}
.card-content {
    display: flex;
    align-items: center;
    padding: 12px 18px;
}
.user-icon {
    font-size: 32px;
    color: #409EFF;
    margin-right: 18px;
}
.user-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
}
.fullname {
    margin-right: 10px;
}
:deep(.el-card__body) {
    --el-card-padding: 0;
}
:deep(.el-tag) {
    font-size: 14px;
    margin: 0 10px;
}
.auth-alert {
  margin: 32px 0;
}
</style>
