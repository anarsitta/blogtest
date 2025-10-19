import { defineStore, storeToRefs } from 'pinia'
import { ref, computed } from 'vue'
import { User } from '@element-plus/icons-vue'
import { useAuthStore } from './auth'
import { useRoute } from 'vue-router'

export const useMenuStore = defineStore('menu', () => {
    const route = useRoute()
    const authStore = useAuthStore()
    const {user} = storeToRefs(authStore)

    const menuItems = ref([
        { key: 'feed', label: 'Лента', icon: null, route: '/feed' },
        { key: 'blacklist', label: 'Черный список', icon: null, route: '/blacklist', requiredAuth: true },
        { key: 'whitelist', label: 'Белый список', icon: null, route: '/whitelist', requiredAuth: true },
        { key: 'profile', label: 'Профиль', icon: User, route: '/profile', requiredAuth: true },
    ])

    // Вычисляемое свойство для отображения только доступных пунктов меню
    const visibleMenuItems = computed(() => {
        return menuItems.value.filter(item => {
            // Если пункт требует авторизации и пользователь не авторизован - скрываем
            if (item.requiredAuth && item.key === 'profile' && !user.value) {
                return false
            }
            return true
        })
    })

    // Показывать warning необходимо авторизоваться
    const showNeedWarningAutoriz = () => {
        console.log(route)
        return !user.value && menuItems.value.some(x => x.key === route.path && x.requiredAuth)
    }

    return {
        menuItems,
        visibleMenuItems,
        showNeedWarningAutoriz
    }
})
