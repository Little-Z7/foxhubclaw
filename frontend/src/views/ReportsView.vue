<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api, fileUrl } from "../api";

const reports = ref<Array<Record<string, any>>>([]);
const runs = ref<Array<Record<string, any>>>([]);

onMounted(async () => {
  reports.value = await api.reports();
  runs.value = await api.runs();
});
</script>

<template>
  <section>
    <h1 class="display">查询报告</h1>
    <div class="card">
      <table>
        <thead>
          <tr>
            <th>关键词</th>
            <th>时间</th>
            <th>下载</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="report in reports" :key="report.id">
            <td>{{ report.keyword }}</td>
            <td>{{ report.created_at }}</td>
            <td class="row">
              <a :href="fileUrl(Number(report.id), 'html')" target="_blank">HTML</a>
              <a :href="fileUrl(Number(report.id), 'xlsx')">Excel</a>
              <a :href="fileUrl(Number(report.id), 'pdf')">PDF</a>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="card">
      <h2>最近运行</h2>
      <p v-for="run in runs" :key="run.id" class="hint">
        #{{ run.id }} {{ run.keyword }} · {{ run.status }} · {{ run.item_count }} 条 · {{ run.message }}
      </p>
    </div>
  </section>
</template>
