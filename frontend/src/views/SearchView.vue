<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
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
const prompts = ref<string[]>([]);
const defaults = ref<string[]>([]);
const editingPrompts = ref(false);
const newPrompt = ref("");
const promptMessage = ref("");

onMounted(async () => {
  const meta = await api.meta();
  platforms.value = meta.platforms;
  selected.value = meta.platforms.filter((p) => p.post).map((p) => p.id);
  defaults.value = meta.default_prompts || [];
  prompts.value = [...defaults.value];
  try {
    const settings = await api.settings();
    prompts.value = settings.prompts;
  } catch {
    /* 未登录时先用内置提示词 */
  }
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

function platformLabel(id: string): string {
  return platforms.value.find((item) => item.id === id)?.name || id;
}

function platformUsable(platform: Platform): boolean {
  return kinds.value.some((kind) => (kind === "comment" ? platform.comment : platform.post));
}

const summary = computed(() => {
  const counts = new Map<string, number>();
  for (const item of items.value) {
    const id = String(item.platform || "");
    counts.set(id, (counts.get(id) || 0) + 1);
  }
  return [...counts.entries()].map(([id, count]) => `${platformLabel(id)} ${count} 条`).join(" · ");
});

function usePrompt(text: string) {
  keyword.value = text;
}

async function persistPrompts(next: string[]) {
  const result = await api.saveSettings({ prompts: next });
  prompts.value = result.prompts;
}

async function addPrompt() {
  const text = newPrompt.value.trim();
  if (!text) return;
  await persistPrompts([...prompts.value, text]);
  newPrompt.value = "";
  promptMessage.value = "已添加";
}

async function removePrompt(text: string) {
  await persistPrompts(prompts.value.filter((item) => item !== text));
}

async function resetPrompts() {
  await persistPrompts([...defaults.value]);
  promptMessage.value = "已恢复默认提示词";
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
    <p class="hint" style="letter-spacing: 0.22em; text-transform: uppercase; color: var(--ember)">即时检索</p>
    <h1 class="display">全网关键词检索</h1>
    <div class="card">
      <div class="row">
        <label class="field">关键词<input v-model="keyword" placeholder="例如：人工智能" /></label>
      </div>
      <div class="prompt-head">
        <p class="hint">常用提示词，点击填入；可自定义增删</p>
        <button class="ghost" type="button" @click="editingPrompts = !editingPrompts">
          {{ editingPrompts ? "完成" : "自定义" }}
        </button>
      </div>
      <div class="prompt-row">
        <button
          v-for="item in prompts"
          :key="item"
          class="chip prompt"
          type="button"
          @click="usePrompt(item)"
        >
          {{ item }}
          <span v-if="editingPrompts" class="prompt-remove" @click.stop="removePrompt(item)">×</span>
        </button>
        <p v-if="!prompts.length" class="hint">还没有提示词，点「自定义」添加，或恢复默认。</p>
      </div>
      <div v-if="editingPrompts" class="row prompt-edit">
        <label class="field">新增提示词<input v-model="newPrompt" placeholder="输入后添加" @keydown.enter.prevent="addPrompt" /></label>
        <button class="primary" type="button" :disabled="!newPrompt.trim()" @click="addPrompt">添加</button>
        <button class="ghost" type="button" @click="resetPrompts">恢复默认</button>
      </div>
      <p v-if="promptMessage" class="hint">{{ promptMessage }}</p>
      <p class="hint">类型</p>
      <label class="chip"><input type="checkbox" :checked="kinds.includes('post')" @change="toggleKind('post')" />帖子 / 作品</label>
      <label class="chip"><input type="checkbox" :checked="kinds.includes('comment')" @change="toggleKind('comment')" />评论</label>
      <p class="hint">平台</p>
      <label
        v-for="platform in platforms"
        :key="platform.id"
        class="chip"
        :class="{ disabled: !platformUsable(platform) }"
      >
        <input
          type="checkbox"
          :disabled="!platformUsable(platform)"
          :checked="selected.includes(platform.id)"
          @change="togglePlatform(platform.id, platformUsable(platform))"
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
      <h2>部分平台未出结果</h2>
      <p v-for="fail in failures" :key="fail.platform + fail.kind" class="hint">
        {{ platformLabel(fail.platform) }} / {{ fail.kind === "post" ? "帖子" : "评论" }}：{{ fail.message }}
      </p>
    </div>
    <div class="card" v-if="items.length">
      <p class="hint">{{ summary }}</p>
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
            <td>{{ platformLabel(String(item.platform)) }}</td>
            <td>{{ item.kind === "comment" ? "评论" : "帖子" }}</td>
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
