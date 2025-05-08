import { createRouter, createWebHistory } from 'vue-router';
import Home from './Home.vue';
import DialyDraw from './DialyDraw.vue';
import Teszt from './Teszt.vue'; // Ha már ezt is használod

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/dialydraw', name: 'DialyDraw', component: DialyDraw },
  { path: '/teszt', name: 'Teszt', component: Teszt }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router;

