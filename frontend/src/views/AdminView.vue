<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api } from "../api";

const users = ref<Array<Record<string, any>>>([]);
const error = ref("");

async function refresh() {
  try {
    users.value = await api.adminUsers();
  } catch (err) {
    error.value = err instanceof Error ? err.message : "无权访问";
  }
}

onMounted(refresh);
</script>

<template>
  <section>
    <h1 class="display">Admin</h1>
    <p v-if="error" class="error">{{ error }}</p>
    <div class="card">
      <table>
        <thead>
          <tr>
            <th>用户</th>
            <th>邮箱</th>
            <th>角色</th>
            <th>状态</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.username }}</td>
            <td>{{ user.email || "-" }}</td>
            <td>{{ user.is_admin ? "Admin" : "User" }}</td>
            <td>{{ user.is_active ? "启用" : "停用" }}</td>
            <td>
              <button class="ghost" @click="api.setActive(Number(user.id), !user.is_active).then(refresh)">
                切换
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
