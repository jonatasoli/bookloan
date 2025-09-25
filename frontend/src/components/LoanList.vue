
<!-- django/frontend/src/components/LoanList.vue -->
<template>
  <div>
    <div v-if="loading">Loading...</div>
    <div v-else-if="items.length === 0">No loans found.</div>
    <table v-else class="loan-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Book</th>
          <th>Borrower</th>
          <th>Loan Date</th>
          <th>Due Date</th>
          <th>Returned</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="loan in items" :key="loan.id">
          <td>{{ loan.id }}</td>
          <td>{{ loan.book_title || loan.book }}</td>
          <td>{{ loan.borrower_name || loan.borrower }}</td>
          <td>{{ loan.loan_date }}</td>
          <td>{{ loan.due_date }}</td>
          <td>{{ loan.returned ? 'Yes' : 'No' }}</td>
          <td>
            <router-link :to="`/loans/${loan.id}/edit`">Edit</router-link>
            <button @click="$emit('delete', loan.id)" class="btn-del">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from "vue";

const props = defineProps<{
  items: Array<Record<string, any>>;
  loading: boolean;
}>();
</script>

<style scoped>
.loan-table { width:100%; border-collapse: collapse; }
.loan-table th, .loan-table td { padding: 0.5rem; border: 1px solid #eee; text-align:left; }
.btn-del { margin-left: 0.5rem; color: #c00; background: none; border: none; cursor: pointer; }
</style>
