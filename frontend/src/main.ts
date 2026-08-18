import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import App from "./App.vue";
import "./styles.css";
import { api, getToken } from "./api";
import SearchView from "./views/SearchView.vue";
import TasksView from "./views/TasksView.vue";
import ReportsView from "./views/ReportsView.vue";
import SettingsView from "./views/SettingsView.vue";
import AdminView from "./views/AdminView.vue";
import LoginView from "./views/LoginView.vue";
import RegisterView from "./views/RegisterView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/search" },
    { path: "/login", component: LoginView, meta: { public: true } },
    { path: "/register", component: RegisterView, meta: { public: true } },
    { path: "/search", component: SearchView },
    { path: "/tasks", component: TasksView },
    { path: "/reports", component: ReportsView },
    { path: "/settings", component: SettingsView },
    { path: "/admin", component: AdminView },
  ],
});

router.beforeEach(async (to) => {
  const meta = await api.meta();
  if (!meta.auth_required || to.meta.public) return true;
  if (!getToken()) return "/login";
  return true;
});

createApp(App).use(router).mount("#app");
