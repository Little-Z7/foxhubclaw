<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { api, setToken } from "../api";

const router = useRouter();
const username = ref("");
const email = ref("");
const password = ref("");
const error = ref("");

async function submit() {
  error.value = "";
  try {
    const result = await api.register({
      username: username.value,
      email: email.value || undefined,
      password: password.value,
    });
    setToken(result.token);
    await router.push("/search");
  } catch (err) {
    error.value = err instanceof Error ? err.message : "注册失败";
  }
}
</script>

<template>
  <div class="auth">
    <div class="card">
      <p class="hint" style="letter-spacing: 0.28em; text-transform: uppercase; color: var(--ember)">FoxHubClaw</p>
      <h1>Create account</h1>
      <label class="field">用户名<input v-model="username" /></label>
      <label class="field" style="margin-top: 12px">邮箱（可选）<input v-model="email" /></label>
      <label class="field" style="margin-top: 12px">密码<input v-model="password" type="password" /></label>
      <p v-if="error" class="error">{{ error }}</p>
      <div class="row" style="margin-top: 18px">
        <button class="primary" @click="submit">注册</button>
        <router-link to="/login">已有账号</router-link>
      </div>
    </div>
  </div>
</template>
