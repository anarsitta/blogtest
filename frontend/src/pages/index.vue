<template>
    <el-text :size="'large'" class="title">BlogTest</el-text>
    <el-text type="info" class="subtitle">
        Современная система управления пользователями и блогами.
    </el-text>

    <el-divider />

    <el-row>
        <span style="color:#409EFF;">Возможности:</span>
        <ul class="main-list">
            <li>Регистрация и авторизация с хранением токенов в cookie</li>
            <li>Профиль пользователя с редактированием информации</li>
            <li>Роли: пользователь, модератор, суперпользователь</li>
            <li>Черный и белый списки</li>
            <li>JWT авторизация, автоматическое обновление сессии</li>
            <li>В будущем: блоги, лента, управление контентом</li>
        </ul>
    </el-row>
</template>

<script setup>
import { useAuthStore } from '../store/auth';
import { storeToRefs } from 'pinia';

const authStore = useAuthStore();
const { showModalAuth } = storeToRefs(authStore);
</script>

<style scoped>
.main-card {
	max-width: 600px;
	margin: 48px auto;
	padding: 32px 24px;
	background: #fff;
	border-radius: 18px;
	box-shadow: 0 4px 24px #409eff22;
}
.main-title {
	font-size: 2.2rem;
	font-weight: bold;
	color: #409EFF;
	margin-bottom: 12px;
}
.main-desc {
	font-size: 1.15rem;
	margin-bottom: 18px;
}
.main-list {
	text-align: left;
	margin: 0 auto 18px auto;
	max-width: 480px;
	font-size: 13px;
	color: #333;
	padding-left: 22px;
}
.main-list li {
	margin-bottom: 8px;
}
</style>
