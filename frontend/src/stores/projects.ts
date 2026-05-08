import { defineStore } from "pinia";
import { ref } from "vue";
import { api } from "@/api";
import type { Project, ProjectDetail } from "@/types";

export const useProjectsStore = defineStore("projects", () => {
  const projects = ref<Project[]>([]);
  const currentProject = ref<ProjectDetail | null>(null);
  const loading = ref(false);

  async function fetchProjects() {
    loading.value = true;
    try {
      projects.value = await api.listProjects();
    } finally {
      loading.value = false;
    }
  }

  async function fetchProject(id: string) {
    loading.value = true;
    try {
      currentProject.value = await api.getProject(id);
    } finally {
      loading.value = false;
    }
  }

  async function createProject(name: string, description?: string) {
    const project = await api.createProject(name, description);
    projects.value.unshift(project);
    return project;
  }

  return { projects, currentProject, loading, fetchProjects, fetchProject, createProject };
});
