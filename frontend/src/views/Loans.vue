<template>
  <section>
    <h2>Book Loans</h2>
    <div class="controls">
      <button @click="fetchLoans">Refresh</button>
      <router-link to="/loans/new"><button>Create Loan</button></router-link>
    </div>

    <loan-list :items="loans" :loading="loading" @delete="handleDelete" />

  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import LoanList from "@/components/LoanList.vue";
import { useRouter } from "vue-router";

const loans = ref<Array<Record<string, any>>>([]);
const loading = ref(false);
const router = useRouter();

async function fetchLoans() {
  loading.value = true;
  try {
    const res = await fetch(import.meta.env.VITE_API_BASE + "/api/bookloans/");
    if (!res.ok) throw new Error("Failed to fetch");
    loans.value = await res.json();
  } catch (err) {
    console.error(err);
    // optionally show toast
  } finally {
    loading.value = false;
  }
}

async function handleDelete(id: number) {
  if (!confirm("Delete loan?")) return;
  try {
    const res = await fetch(`${import.meta.env.VITE_API_BASE}/api/bookloans/${id}/`, {
      method: "DELETE",
    });
    if (res.ok) {
      // remove locally
      loans.value = loans.value.filter(l => l.id !== id);
    } else {
      alert("Delete failed");
    }
  } catch (err) {
    console.error(err);
    alert("Delete failed");
  }
}

onMounted(fetchLoans);
</script>

<style scoped>
.controls { margin-bottom: 1rem; }
</style>
