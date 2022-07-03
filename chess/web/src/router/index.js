import { createWebHistory, createRouter } from 'vue-router'

import Main from '@/views/Main.vue'
import Rule from '@/views/Rule.vue'

const routes = [
    {
        path: '/',
        component: Main,
        name: 'Main',
        meta: {
            title: '量子国际象棋',
        }
    },
    {
        path: '/rule',
        component: Rule,
        name: 'Rule',
        meta: {
            title: '说明文档',
        }
    },
]

const router = createRouter({
    // https://next.router.vuejs.org/guide/essentials/history-mode.html
    history: createWebHistory(),
    routes
})

export default router