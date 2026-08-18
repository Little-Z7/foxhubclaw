<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { api, setToken } from "../api";

const router = useRouter();
const login = ref("");
const password = ref("");
const error = ref("");

async function submit() {
  error.value = "";
  try {
    const result = await api.login({ login: login.value, password: password.value });
    setToken(result.token);
    await router.push("/search");
  } catch (err) {
    error.value = err instanceof Error ? err.message : "登录失败";
  }
}
</script>

<template>
  <div class="auth">
    <div class="card">
      <p class="hint" style="letter-spacing: 0.28em; text-transform: uppercase; color: var(--ember)">FoxHubClaw</p>
      <h1>Sign in</h1>
      <p class="hint">用邮箱或用户名进入查询台</p>
      <label class="field">登录名<input v-model="login" /></label>
      <label class="field" style="margin-top: 12px">密码<input v-model="password" type="password" /></label>
      <p v-if="error" class="error">{{ error }}</p>
      <div class="row" style="margin-top: 18px">
        <button class="primary" @click="submit">进入</button>
        <router-link to="/register">创建账号</router-link>
      </div>
    </div>
  </div>
</template>
