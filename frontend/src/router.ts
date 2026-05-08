import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "projects",
      component: () => import("@/views/ProjectList.vue"),
    },
    {
      path: "/projects/:id",
      name: "project-detail",
      component: () => import("@/views/ProjectDetail.vue"),
    },
    {
      path: "/projects/:id/chat",
      name: "project-chat",
      component: () => import("@/views/ProjectChat.vue"),
    },
    {
      path: "/projects/:id/consolidate",
      name: "project-consolidate",
      component: () => import("@/views/ProjectConsolidate.vue"),
    },
  ],
});

export default router;
