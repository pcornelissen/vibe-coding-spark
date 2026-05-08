<script setup lang="ts">
import Button from "primevue/button";
import Card from "primevue/card";
import Dialog from "primevue/dialog";
import InputText from "primevue/inputtext";
import Textarea from "primevue/textarea";
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useProjectsStore } from "@/stores/projects";

const store = useProjectsStore();
const router = useRouter();
const showDialog = ref(false);
const newName = ref("");
const newDescription = ref("");

onMounted(() => store.fetchProjects());

async function createProject() {
  if (!newName.value.trim()) return;
  const project = await store.createProject(newName.value.trim(), newDescription.value.trim() || undefined);
  showDialog.value = false;
  newName.value = "";
  newDescription.value = "";
  router.push({ name: "project-detail", params: { id: project.id } });
}
</script>

<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem">
      <h2 style="margin: 0">Projekte</h2>
      <Button label="Neues Projekt" icon="pi pi-plus" @click="showDialog = true" />
    </div>

    <div v-if="store.loading">Laedt...</div>

    <div v-else-if="store.projects.length === 0" style="text-align: center; padding: 3rem; color: var(--p-text-muted-color)">
      <p>Noch keine Projekte vorhanden.</p>
      <Button label="Erstes Projekt anlegen" icon="pi pi-plus" @click="showDialog = true" />
    </div>

    <div v-else style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem">
      <Card
        v-for="project in store.projects"
        :key="project.id"
        style="cursor: pointer"
        @click="router.push({ name: 'project-detail', params: { id: project.id } })"
      >
        <template #title>{{ project.name }}</template>
        <template #subtitle>{{ project.document_count }} Dokument(e)</template>
        <template #content>
          <p v-if="project.description">{{ project.description }}</p>
        </template>
      </Card>
    </div>

    <Dialog v-model:visible="showDialog" header="Neues Projekt" modal style="width: 30rem">
      <div style="display: flex; flex-direction: column; gap: 1rem">
        <div>
          <label for="name">Name</label>
          <InputText id="name" v-model="newName" style="width: 100%" autofocus />
        </div>
        <div>
          <label for="desc">Beschreibung (optional)</label>
          <Textarea id="desc" v-model="newDescription" rows="3" style="width: 100%" />
        </div>
      </div>
      <template #footer>
        <Button label="Abbrechen" severity="secondary" @click="showDialog = false" />
        <Button label="Anlegen" @click="createProject" :disabled="!newName.trim()" />
      </template>
    </Dialog>
  </div>
</template>
