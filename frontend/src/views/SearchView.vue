<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api, type Platform } from "../api";

const platforms = ref<Platform[]>([]);
const keyword = ref("");
const selected = ref<string[]>([]);
const kinds = ref<string[]>(["post"]);
const items = ref<Array<Record<string, any>>>([]);
const failures = ref<Array<{ platform: string; kind: string; message: string }>>([]);
const status = ref("");
const error = ref("");
const loading = ref(false);

onMounted(async () => {
  const meta = await api.meta();
  platforms.value = meta.platforms;
  selected.value = meta.platforms.filter((p) => p.post).map((p) => p.id);
});

function togglePlatform(id: string, enabled: boolean) {
  if (!enabled) return;
  selected.value = selected.value.includes(id)
    ? selected.value.filter((item) => item !== id)
    : [...selected.value, id];
}

function toggleKind(kind: string) {
  kinds.value = kinds.value.includes(kind) ? kinds.value.filter((item) => item !== kind) : [...kinds.value, kind];
}

async function runSearch() {
  error.value = "";
  loading.value = true;
  try {
    const result = await api.search({
      keyword: keyword.value,
      platforms: selected.value,
      kinds: kinds.value,
    });
    items.value = result.items;
    failures.value = result.failures;
    status.value = `状态 ${result.status} · ${result.items.length} 条 · 报告 #${result.report_id}`;
  } catch (err) {
    error.value = err instanceof Error ? err.message : "查询失败";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <section>
    <p class="hint" style="letter-spacing: 0.22em; text-transform: uppercase; color: var(--ember)">Live wire</p>
    <h1 class="display">全网关键词检索</h1>
    <div class="card">
      <div class="row">
        <label class="field">关键词<input v-model="keyword" placeholder="例如：人工智能" /></label>
      </div>
      <p class="hint">类型</p>
      <label class="chip"><input type="checkbox" :checked="kinds.includes('post')" @change="toggleKind('post')" />帖子 / 作品</label>
      <label class="chip"><input type="checkbox" :checked="kinds.includes('comment')" @change="toggleKind('comment')" />评论</label>
      <p class="hint">平台</p>
      <label
        v-for="platform in platforms"
        :key="platform.id"
        class="chip"
        :class="{ disabled: kinds.includes('comment') ? !platform.comment : !platform.post }"
      >
        <input
          type="checkbox"
          :disabled="kinds.includes('comment') ? !platform.comment : !platform.post"
          :checked="selected.includes(platform.id)"
          @change="togglePlatform(platform.id, kinds.includes('comment') ? platform.comment : platform.post)"
        />
        {{ platform.name }}
        <small v-if="kinds.includes('comment') && !platform.comment">{{ platform.comment_note }}</small>
        <small v-else-if="!platform.post">暂不支持帖子</small>
      </label>
      <div class="row" style="margin-top: 16px">
        <button class="primary" :disabled="loading || !keyword" @click="runSearch">
          {{ loading ? "查询中…" : "开始查询" }}
        </button>
      </div>
      <p v-if="status" class="hint">{{ status }}</p>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
    <div class="card" v-if="failures.length">
      <h2>部分失败</h2>
      <p v-for="fail in failures" :key="fail.platform + fail.kind" class="hint">
        {{ fail.platform }} / {{ fail.kind }}：{{ fail.message }}
      </p>
    </div>
    <div class="card" v-if="items.length">
      <table>
        <thead>
          <tr>
            <th>平台</th>
            <th>类型</th>
            <th>标题</th>
            <th>作者</th>
            <th>点赞</th>
            <th>时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in items" :key="index">
            <td>{{ item.platform }}</td>
            <td>{{ item.kind }}</td>
            <td>
              <a v-if="item.url" :href="String(item.url)" target="_blank">{{ item.title }}</a>
              <span v-else>{{ item.title }}</span>
            </td>
            <td>{{ item.author }}</td>
            <td>{{ item.likes }}</td>
            <td>{{ item.published_at }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
