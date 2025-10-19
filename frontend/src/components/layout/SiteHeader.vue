<template>
    <el-row class="header-row" justify="center" align="middle">
        <div class="logo" @click="router.push('/')">
            <el-icon><ChatDotSquare/></el-icon>
            <span class="logo-title">BlogTest</span>
        </div>
        
        <el-menu mode="horizontal" :ellipsis="false" @select="handleMenuSelect">
            <el-menu-item v-for="item in visibleMenuItems" :key="item.key" :index="item.key">
                <el-icon v-if="item.icon"><component :is="item.icon" /></el-icon>
                {{ item.label }}
            </el-menu-item>

            <div class="user-section">
                <el-menu-item v-if="!user" class="login-button" index="login" @click="showModalAuth = true">
                    <el-icon><User/></el-icon>
                    Войти
                </el-menu-item>
                
                <div v-else class="user-info">
                    <el-button 
                        class="logout-button" 
                        type="primary" 
                        @click="handleLogout"
                    >
                        Выйти
                    </el-button>
                </div>
            </div>
        </el-menu>
    </el-row>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMenu, ElMenuItem, ElIcon, ElButton } from 'element-plus'
import { ChatDotSquare, User } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { storeToRefs } from 'pinia'
import { useMenuStore } from '@/store/menu'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const menuStore = useMenuStore()
const { showModalAuth, user } = storeToRefs(authStore)
const { menuItems, visibleMenuItems }  = storeToRefs(menuStore)

const activeKey = ref('feed')
function updateActiveFromRoute(path) {
    const item = menuItems.value.find(i => i.route === path)
    if (item) activeKey.value = item.key
    else if (path === '/' || path === '') activeKey.value = 'feed'
}

updateActiveFromRoute(route.path)
watch(() => route.path, (p) => updateActiveFromRoute(p))

function handleMenuSelect(key) {
    const item = menuItems.value.find(i => i.key === key)
    if (!item) return
    if (item.requiredAuth && !user.value) {
        showModalAuth.value = true
    }
    if (item) {
        activeKey.value = key
        router.push(item.route)
    }
}

function handleLogout() {
    // Вызов метода выхода из хранилища auth
    authStore.logout()
    // Перенаправление на главную страницу
    router.push('/')
}
</script>

<style scoped>
.logo-title {
    font-size: 1.5rem;
    font-weight: bold;
    color: #409EFF;
    letter-spacing: 1px;
}

:deep(.logo .el-icon) {
    font-size: 31px;
    vertical-align: middle;
    color: var(--el-color-primary);
    padding-right: 4px;
    margin-bottom: 7px;
}

.logo {
    padding-right: 30px;
    padding-left: 26px;
    line-height: 56px;
}

.logo:hover {
    cursor: pointer;
    background-color: var(--el-color-primary-light-9);
}

:deep(.el-menu-item) {
    font-size: 16px !important;
    font-weight: 500;
    height: 60px !important;
}

.user-section {
    display: flex;
    align-items: center;
    margin-left: auto;
}

.user-info {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0 16px;
}

.user-name {
    font-size: 14px;
    color: var(--el-text-color-primary);
    font-weight: 500;
}

.logout-button {
    display: flex;
    align-items: center;
    gap: 6px;
    height: 32px;
    font-size: 14px;
}

.logout-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

/* Адаптивность для мобильных устройств */
@media (max-width: 768px) {
    .user-info {
        flex-direction: column;
        gap: 8px;
        padding: 8px 12px;
    }
    
    .user-name {
        font-size: 13px;
    }
    
    .logout-button {
        height: 28px;
        font-size: 13px;
    }
}
</style>