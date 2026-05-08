<script setup lang="ts">
import Button from "primevue/button";
import Card from "primevue/card";
import InputText from "primevue/inputtext";
import SelectButton from "primevue/selectbutton";
import Tag from "primevue/tag";
import { marked } from "marked";
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { api } from "@/api";
import type { ConsolidationResult, ResultType } from "@/types";

const route = useRoute();
const projectId = route.params.id as string;

const resultTypeOptions = [
  { label: "Zusammenfassung", value: "summary" },
  { label: "Widersprueche", value: "contradiction" },
  { label: "Konsolidierung", value: "consolidation" },
];

const selectedType = ref<ResultType>("summary");
const query = ref("");
const streaming = ref(false);
const streamContent = ref("");
const savedResults = ref<ConsolidationResult[]>([]);

onMounted(loadResults);

async function loadResults() {
  savedResults.value = await api.getResults(projectId);
}

function startConsolidation() {
  if (!query.value.trim() || streaming.value) return;
  streaming.value = true;
  streamContent.value = "";

  const source = api.streamConsolidate(projectId, selectedType.value, query.value.trim());

  source.addEventListener("token", (e: MessageEvent) => {
    streamContent.value += e.data;
  });

  source.addEventListener("done", () => {
    source.close();
    streaming.value = false;
    loadResults();
  });

  source.onerror = () => {
    source.close();
    streaming.value = false;
  };
}

function renderMarkdown(content: string): string {
  return marked.parse(content) as string;
}

const resultTypeLabels: Record<string, string> = {
  summary: "Zusammenfassung",
  contradiction: "Widerspruchsanalyse",
  consolidation: "Konsolidierung",
};
</script>

<template>
  <div>
    <h2>Konsolidierung</h2>

    <div style="display: flex; flex-direction: column; gap: 1rem; margin-bottom: 2rem">
      <SelectButton v-model="selectedType" :options="resultTypeOptions" option-label="label" option-value="value" />

      <div style="display: flex; gap: 0.5rem">
        <InputText
          v-model="query"
          :placeholder="
            selectedType === 'contradiction'
              ? 'Welches Thema soll auf Widersprueche geprueft werden?'
              : selectedType === 'summary'
                ? 'Welches Thema soll zusammengefasst werden?'
                : 'Was soll konsolidiert werden?'
          "
          style="flex: 1"
          @keyup.enter="startConsolidation"
          :disabled="streaming"
        />
        <Button label="Starten" icon="pi pi-play" @click="startConsolidation" :loading="streaming" :disabled="!query.trim()" />
      </div>
    </div>

    <Card v-if="streamContent" style="margin-bottom: 2rem">
      <template #title>Aktuelles Ergebnis</template>
      <template #content>
        <div v-html="renderMarkdown(streamContent)" />
        <span v-if="streaming" class="cursor">|</span>
      </template>
    </Card>

    <div v-if="savedResults.length > 0">
      <h3>Gespeicherte Ergebnisse</h3>
      <Card v-for="result in savedResults" :key="result.id" style="margin-bottom: 1rem">
        <template #title>
          <Tag :value="resultTypeLabels[result.result_type] || result.result_type" />
          {{ result.query }}
        </template>
        <template #subtitle>{{ new Date(result.created_at).toLocaleString("de-DE") }}</template>
        <template #content>
          <div v-html="renderMarkdown(result.result_content)" />
        </template>
      </Card>
    </div>
  </div>
</template>

<style>
.cursor {
  animation: blink 1s step-end infinite;
}
@keyframes blink {
  50% { opacity: 0; }
}
</style>
