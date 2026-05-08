<script setup lang="ts">
import { RouterView } from "vue-router";
</script>

<template>
  <div class="layout">
    <header class="layout-header">
      <h1>Spark Docs</h1>
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
  padding: 1rem 2rem;
  background: var(--p-primary-color);
  color: var(--p-primary-contrast-color);
}

.layout-header h1 {
  margin: 0;
  font-size: 1.25rem;
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
