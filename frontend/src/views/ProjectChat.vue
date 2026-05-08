<script setup lang="ts">
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import { ref } from "vue";
import { useRoute } from "vue-router";
import { api } from "@/api";

const route = useRoute();
const projectId = route.params.id as string;

interface Message {
  role: "user" | "assistant";
  content: string;
}

const messages = ref<Message[]>([]);
const input = ref("");
const streaming = ref(false);

function sendMessage() {
  const question = input.value.trim();
  if (!question || streaming.value) return;

  messages.value.push({ role: "user", content: question });
  input.value = "";
  streaming.value = true;

  const assistantMsg: Message = { role: "assistant", content: "" };
  messages.value.push(assistantMsg);

  const source = api.streamChat(projectId, question);

  source.addEventListener("token", (e: MessageEvent) => {
    assistantMsg.content += e.data;
  });

  source.addEventListener("done", () => {
    source.close();
    streaming.value = false;
  });

  source.onerror = () => {
    source.close();
    streaming.value = false;
    if (!assistantMsg.content) {
      assistantMsg.content = "Fehler bei der Verbindung zum Server.";
    }
  };
}
</script>

<template>
  <div style="display: flex; flex-direction: column; height: calc(100vh - 10rem)">
    <h2>Chat</h2>

    <div style="flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 0.75rem; padding: 1rem 0">
      <div
        v-for="(msg, i) in messages"
        :key="i"
        :style="{
          alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
          background: msg.role === 'user' ? 'var(--p-primary-color)' : 'var(--p-surface-200)',
          color: msg.role === 'user' ? 'var(--p-primary-contrast-color)' : 'var(--p-text-color)',
          padding: '0.75rem 1rem',
          borderRadius: '0.75rem',
          maxWidth: '70%',
          whiteSpace: 'pre-wrap',
        }"
      >
        {{ msg.content }}<span v-if="streaming && i === messages.length - 1 && msg.role === 'assistant'" class="cursor">|</span>
      </div>
    </div>

    <div style="display: flex; gap: 0.5rem; padding-top: 0.5rem">
      <InputText
        v-model="input"
        placeholder="Frage an die Dokumente..."
        style="flex: 1"
        @keyup.enter="sendMessage"
        :disabled="streaming"
      />
      <Button icon="pi pi-send" @click="sendMessage" :disabled="!input.trim() || streaming" />
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
