<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api } from "../api";

const apiKey = ref("");
const masked = ref("");
const limit = ref(20);
const depth = ref(3);
const message = ref("");

onMounted(async () => {
  const data = await api.settings();
  masked.value = data.api_key_masked;
  limit.value = data.limit_per_platform;
  depth.value = data.comment_depth;
});

async function save() {
  const body: Record<string, unknown> = {
    limit_per_platform: limit.value,
    comment_depth: depth.value,
  };
  if (apiKey.value.trim()) body.api_key = apiKey.value.trim();
  const result = (await api.saveSettings(body)) as { api_key_masked: string };
  masked.value = result.api_key_masked;
  apiKey.value = "";
  message.value = "已保存";
}
</script>

<template>
  <section>
    <h1 class="display">Settings</h1>
    <div class="card">
      <p class="hint">当前 Key：{{ masked || "未填写" }}</p>
      <label class="field">RedFox API Key<input v-model="apiKey" placeholder="粘贴新的 Key，留空则不改" /></label>
      <div class="row" style="margin-top: 12px">
        <label class="field">每平台条数<input v-model.number="limit" type="number" min="1" max="100" /></label>
        <label class="field">评论下钻条数<input v-model.number="depth" type="number" min="1" max="10" /></label>
      </div>
      <button class="primary" style="margin-top: 16px" @click="save">保存</button>
      <p v-if="message" class="hint">{{ message }}</p>
    </div>
  </section>
</template>
