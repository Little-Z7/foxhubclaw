<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { api, setToken, type Meta } from "./api";

const route = useRoute();
const meta = ref<Meta | null>(null);
const username = ref("");
const isAdmin = ref(false);

onMounted(async () => {
  meta.value = await api.meta();
  if (!meta.value.auth_required || route.path === "/login" || route.path === "/register") return;
  try {
    const me = await api.me();
    username.value = me.username;
    isAdmin.value = me.is_admin;
  } catch {
    setToken("");
  }
});

function logout() {
  setToken("");
  window.location.href = "/login";
}
</script>

<template>
  <div v-if="route.path === '/login' || route.path === '/register'">
    <router-view />
  </div>
  <div v-else class="shell">
    <aside class="rail">
      <div class="brand">
        <img class="brand-mark" src="/favicon.ico" alt="" width="40" height="40" />
        <small>红狐查询台</small>
        <strong>FoxHubClaw</strong>
      </div>
      <nav>
        <router-link to="/search">即时查询</router-link>
        <router-link to="/tasks">定时任务</router-link>
        <router-link to="/reports">查询报告</router-link>
        <router-link to="/settings">设置</router-link>
        <router-link v-if="isAdmin && meta?.auth_required" to="/admin">后台管理</router-link>
      </nav>
      <p class="hint" style="margin-top: 40px">{{ username || (meta?.mode === "desktop" ? "桌面版" : "") }}</p>
      <button v-if="meta?.auth_required" class="ghost" style="margin-top: 12px" @click="logout">退出登录</button>
    </aside>
    <main class="stage">
      <router-view />
    </main>
  </div>
</template>
