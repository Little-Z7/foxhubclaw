<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api, downloadReportFile, fileUrl } from "../api";

const reports = ref<Array<Record<string, any>>>([]);
const runs = ref<Array<Record<string, any>>>([]);
const error = ref("");
const message = ref("");
const busy = ref("");

onMounted(async () => {
  try {
    reports.value = await api.reports();
    runs.value = await api.runs();
  } catch (err) {
    error.value = err instanceof Error ? err.message : "加载报告失败";
  }
});

async function download(reportId: number, kind: "xlsx" | "pdf") {
  error.value = "";
  message.value = "";
  busy.value = `${reportId}-${kind}`;
  try {
    const name = await downloadReportFile(reportId, kind);
    message.value = `已开始下载 ${name}`;
  } catch (err) {
    error.value = err instanceof Error ? err.message : "下载失败";
  } finally {
    busy.value = "";
  }
}
</script>

<template>
  <section>
    <h1 class="display">查询报告</h1>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="message" class="hint">{{ message }}</p>
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
              <a :href="fileUrl(Number(report.id), 'html')" target="_blank" rel="noopener">HTML</a>
              <button
                class="ghost"
                type="button"
                :disabled="busy === `${report.id}-xlsx`"
                @click="download(Number(report.id), 'xlsx')"
              >
                {{ busy === `${report.id}-xlsx` ? "下载中…" : "Excel" }}
              </button>
              <button
                class="ghost"
                type="button"
                :disabled="busy === `${report.id}-pdf`"
                @click="download(Number(report.id), 'pdf')"
              >
                {{ busy === `${report.id}-pdf` ? "下载中…" : "PDF" }}
              </button>
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
