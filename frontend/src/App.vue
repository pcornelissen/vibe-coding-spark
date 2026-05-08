<script setup lang="ts">
import Button from "primevue/button";
import { RouterView, useRouter } from "vue-router";

const router = useRouter();
</script>

<template>
  <div class="layout">
    <header class="layout-header">
      <Button
        text
        style="color: var(--p-primary-contrast-color); font-size: 1.25rem; font-weight: bold"
        @click="router.push('/')"
      >
        Spark Docs
      </Button>
    </header>
    <main class="layout-main">
      <RouterView />
    </main>
  </div>
</template>

<style>
body {
  margin: 0;
  font-family: var(--p-font-family);
  background: var(--p-surface-ground);
  color: var(--p-text-color);
}

.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-header {
  padding: 0.5rem 2rem;
  background: var(--p-primary-color);
  display: flex;
  align-items: center;
}

.layout-main {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}
</style>
