<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api, type Platform } from "../api";

const platforms = ref<Platform[]>([]);
const tasks = ref<Array<Record<string, any>>>([]);
const keyword = ref("");
const cadence = ref("daily");
const selected = ref<string[]>([]);
const kinds = ref<string[]>(["post"]);
const error = ref("");

async function refresh() {
  tasks.value = await api.tasks();
}

onMounted(async () => {
  const meta = await api.meta();
  platforms.value = meta.platforms.filter((p) => p.post);
  selected.value = platforms.value.map((p) => p.id);
  await refresh();
});

async function createTask() {
  error.value = "";
  try {
    await api.createTask({
      keyword: keyword.value,
      platforms: selected.value,
      kinds: kinds.value,
      cadence: cadence.value,
    });
    keyword.value = "";
    await refresh();
  } catch (err) {
    error.value = err instanceof Error ? err.message : "创建失败";
  }
}
</script>

<template>
  <section>
    <h1 class="display">定时任务</h1>
    <div class="card">
      <div class="row">
        <label class="field">关键词<input v-model="keyword" /></label>
        <label class="field">周期
          <select v-model="cadence">
            <option value="daily">每天</option>
            <option value="weekly">每周</option>
          </select>
        </label>
      </div>
      <p class="hint">保存后按周期自动查询并生成报告。服务或 EXE 运行时每分钟检查到期任务。</p>
      <button class="primary" :disabled="!keyword" @click="createTask">创建任务</button>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
    <div class="card">
      <table>
        <thead>
          <tr>
            <th>名称</th>
            <th>周期</th>
            <th>下次运行</th>
            <th>状态</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in tasks" :key="task.id">
            <td>{{ task.keyword }}</td>
            <td>{{ task.cadence }}</td>
            <td>{{ task.next_run_at || "-" }}</td>
            <td>{{ task.enabled ? "开启" : "暂停" }}</td>
            <td><button class="ghost" @click="api.toggleTask(Number(task.id)).then(refresh)">切换</button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
