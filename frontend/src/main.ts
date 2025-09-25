import { createApp } from "vue";
import App from "./App.vue";
import { createRouter, createWebHistory } from "vue-router";

import Home from "@/views/Home.vue";
import Loans from "@/views/Loans.vue";
import LoanForm from "@/views/LoanForm.vue";

const routes = [
  { path: "/", component: Home },
  { path: "/loans", component: Loans },
  { path: "/loans/new", component: LoanForm },
  { path: "/loans/:id/edit", component: LoanForm, props: true },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

createApp(App).use(router).mount("#app");
