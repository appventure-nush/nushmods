import Vue from 'vue'
import VueRouter, { RouteConfig } from 'vue-router'
import HomeView from '../views/HomeView.vue'

Vue.use(VueRouter)

const routes: Array<RouteConfig> = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  {
    path: '/modules',
    name: 'modules',
    component: () => import(/* webpackChunkName: "modules" */ '../views/ModulesView.vue')
  },
  {
    path: '/departments',
    name: 'departments',
    component: () => import(/* webpackChunkName: "departments" */ '../views/DepartmentsView.vue')
  },
  {
    path: '/departments/:code',
    name: 'departmentDetails',
    component: () => import(/* webpackChunkName: "departments" */ '../views/DepartmentDetailsView.vue')
  },
  {
    path: '/planner',
    name: 'planner',
    component: () => import(/* webpackChunkName: "departments" */ '../views/PlannerView.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
