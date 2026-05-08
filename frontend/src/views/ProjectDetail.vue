<script setup lang="ts">
import Badge from "primevue/badge";
import Button from "primevue/button";
import Column from "primevue/column";
import DataTable from "primevue/datatable";
import FileUpload from "primevue/fileupload";
import Tag from "primevue/tag";
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { api } from "@/api";
import { useProjectsStore } from "@/stores/projects";

const route = useRoute();
const router = useRouter();
const store = useProjectsStore();
const projectId = route.params.id as string;
const uploading = ref(false);
const processing = ref(false);

onMounted(() => store.fetchProject(projectId));

const project = computed(() => store.currentProject);

const statusSeverity: Record<string, string> = {
  pending: "warn",
  uploaded: "info",
  processing: "info",
  ready: "success",
  failed: "danger",
};

async function onUpload(event: { files: File[] }) {
  uploading.value = true;
  try {
    await api.uploadDocuments(projectId, event.files);
    await store.fetchProject(projectId);
  } finally {
    uploading.value = false;
  }
}

async function startProcessing() {
  processing.value = true;
  try {
    await api.startProcessing(projectId);
    await store.fetchProject(projectId);
  } finally {
    processing.value = false;
  }
}
</script>

<template>
  <div v-if="project">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem">
      <div>
        <h2 style="margin: 0">{{ project.name }}</h2>
        <p v-if="project.description" style="color: var(--p-text-muted-color); margin: 0.25rem 0 0">
          {{ project.description }}
        </p>
      </div>
      <div style="display: flex; gap: 0.5rem">
        <Button
          label="Chat"
          icon="pi pi-comments"
          severity="secondary"
          @click="router.push({ name: 'project-chat', params: { id: projectId } })"
        />
        <Button
          label="Konsolidierung"
          icon="pi pi-sync"
          severity="secondary"
          @click="router.push({ name: 'project-consolidate', params: { id: projectId } })"
        />
      </div>
    </div>

    <div style="margin-bottom: 1.5rem">
      <h3>Dokumente</h3>
      <FileUpload
        mode="basic"
        :multiple="true"
        accept=".pdf,.docx,.md,.txt,.xlsx"
        :auto="true"
        choose-label="Dokumente hochladen"
        :disabled="uploading"
        @select="onUpload"
      />
    </div>

    <DataTable :value="project.documents" v-if="project.documents.length > 0">
      <Column field="filename" header="Dateiname" />
      <Column field="format" header="Format">
        <template #body="{ data }">
          <Badge :value="data.format" />
        </template>
      </Column>
      <Column field="upload_status" header="Status">
        <template #body="{ data }">
          <Tag :value="data.upload_status" :severity="statusSeverity[data.upload_status]" />
        </template>
      </Column>
    </DataTable>

    <div v-if="project.documents.length > 0" style="margin-top: 1rem">
      <Button
        label="Verarbeitung starten"
        icon="pi pi-play"
        :loading="processing"
        @click="startProcessing"
      />
    </div>

    <div v-if="project.workflows.length > 0" style="margin-top: 1.5rem">
      <h3>Workflows</h3>
      <DataTable :value="project.workflows">
        <Column field="spark_workflow_id" header="Workflow ID" />
        <Column field="status" header="Status">
          <template #body="{ data }">
            <Tag
              :value="data.status"
              :severity="data.status === 'completed' ? 'success' : data.status === 'failed' ? 'danger' : 'info'"
            />
          </template>
        </Column>
        <Column field="started_at" header="Gestartet" />
      </DataTable>
    </div>
  </div>

  <div v-else>Laedt...</div>
</template>
