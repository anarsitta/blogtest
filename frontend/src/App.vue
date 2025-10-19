<template>
  <el-container>
    <el-header>
      <SiteHeader/>
    </el-header>
    <el-main>
      <el-row justify="center" style="width: 100%; height: 100%;">
        <el-col :span="17" class="col-border">      
          <router-view/>

          <AuthModal v-model:visible="showModalAuth"/>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup>
import SiteHeader from './components/layout/SiteHeader.vue';
import { storeToRefs } from 'pinia';
import { useAuthStore } from './store/auth';
import AuthModal from './components/auth/AuthModal.vue';

const authStore = useAuthStore();
const { showModalAuth } = storeToRefs(authStore);
</script>

<style>
:root {
  font-family: Roboto, sans-serif !important;
}
body {
  margin: 0;
}
.title {
  font-weight: 500;
  font-size: 20px !important;
  width: 100%;
}
.subtitle {
    display: block;
    margin-top: 6px !important;
    margin-bottom: 18px !important;
}
</style>
<style scoped>
:deep(.el-header) {
  min-width: 776px;
}
:deep(.el-main) {
  height: calc(100vh - 80px);
  background-color: #f3f9ff;
  padding: 0 20px;
}
:deep(.el-header) {
  border-bottom: 1px solid var(--el-menu-border-color);
}
.col-border {
  border: 1px solid var(--el-border-color);
  padding: 20px;
  background: white;
  margin: 20px 0;
  border-radius: 10px;
}
</style>
