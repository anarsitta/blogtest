<!-- EditProfileModal.vue -->
<template>
  <el-dialog
    :model-value="visible"
    title="Редактировать профиль"
    width="400px"
    :before-close="handleClose"
  >
    <el-form :model="form" v-if="user" label-position="top">
      <el-form-item label="Никнейм">
        <el-input v-model="form.username" />
      </el-form-item>
      <el-form-item label="Имя">
        <el-input v-model="form.first_name" />
      </el-form-item>
      <el-form-item label="Фамилия">
        <el-input v-model="form.last_name" />
      </el-form-item>
      <el-form-item label="Email">
        <el-input v-model="form.email" />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="handleClose">Отмена</el-button>
      <el-button 
        type="primary" 
        @click="handleSave" 
        :loading="loading"
      >
        Сохранить
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    required: true
  },
  user: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'save'])

const form = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: ''
})

// Синхронизируем форму с данными пользователя
watch(() => props.user, (user) => {
  if (user) {
    form.value.username = user.username || ''
    form.value.email = user.email || ''
    form.value.first_name = user.first_name || ''
    form.value.last_name = user.last_name || ''
  }
}, { immediate: true })

const handleClose = () => {
  emit('update:visible', false)
}

const handleSave = () => {
  emit('save', { ...form.value })
}
</script>