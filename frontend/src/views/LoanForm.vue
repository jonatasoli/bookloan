<template>
  <section>
    <h2>{{ isEdit ? "Edit Loan" : "Create Loan" }}</h2>

    <form @submit.prevent="submit">
      <div>
        <label>Book (title or id)</label>
        <input v-model="form.book" required />
      </div>

      <div>
        <label>Borrower (name or id)</label>
        <input v-model="form.borrower" required />
      </div>

      <div>
        <label>Loan date</label>
        <input type="date" v-model="form.loan_date" />
      </div>

      <div>
        <label>Due date</label>
        <input type="date" v-model="form.due_date" />
      </div>

      <div>
        <label>Returned</label>
        <input type="checkbox" v-model="form.returned" />
      </div>

      <div style="margin-top:1rem;">
        <button type="submit">{{ isEdit ? "Save" : "Create" }}</button>
        <router-link to="/loans"><button type="button">Cancel</button></router-link>
      </div>
    </form>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();
const id = route.params.id;
const isEdit = Boolean(id);

const form = ref<any>({
  book: "",
  borrower: "",
  loan_date: "",
  due_date: "",
  returned: false,
});

async function load() {
  if (!isEdit) return;
  try {
    const res = await fetch(`${import.meta.env.VITE_API_BASE}/api/bookloans/${id}/`);
    if (!res.ok) throw new Error("Failed to load");
    const data = await res.json();
    form.value = { ...data };
  } catch (err) {
    console.error(err);
    alert("Failed to load loan");
  }
}

async function submit() {
  try {
    const url = isEdit
      ? `${import.meta.env.VITE_API_BASE}/api/bookloans/${id}/`
      : `${import.meta.env.VITE_API_BASE}/api/bookloans/`;
    const method = isEdit ? "PUT" : "POST";
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form.value),
    });
    if (!res.ok) throw new Error("Save failed");
    router.push("/loans");
  } catch (err) {
    console.error(err);
    alert("Save failed");
  }
}

onMounted(load);
</script>

<style scoped>
form div { margin-bottom: 0.5rem; }
label { display:block; font-weight:600; margin-bottom:0.25rem; }
input[type="text"], input[type="date"], input { padding: 0.25rem; width:300px; }
</style>
