import Aura from "@primeuix/themes/aura";
import "primeicons/primeicons.css";
import PrimeVue from "primevue/config";
import { createPinia } from "pinia";
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

const app = createApp(App);
app.use(router);
app.use(createPinia());
app.use(PrimeVue, {
  theme: {
    preset: Aura,
  },
});
app.mount("#app");
