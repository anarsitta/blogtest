import { createRouter, createWebHistory } from 'vue-router'
import Index from './pages/index.vue'
import FeedPage from './pages/feed.vue'
import BlacklistPage from './pages/blacklist.vue'
import WhitelistPage from './pages/whitelist.vue'
import ProfilePage from './pages/profile.vue'
import AuthorPage from './pages/author-profile.vue'
import CreatePost from './pages/CreatePost.vue'

const routes = [
  { path: '/', component: Index },
  { path: '/feed', component: FeedPage },
  { path: '/blacklist', component: BlacklistPage },
  { path: '/whitelist', component: WhitelistPage },
  { path: '/create-post', component: CreatePost },
  { path: '/profile', component: ProfilePage },
  { path: '/profile/:username', component: AuthorPage }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router