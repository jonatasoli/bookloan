<template>
  <div id="app" class="app-container">
    <header class="header">
      <h1>BookLoan Admin</h1>
      <nav>
        <router-link to="/">Home</router-link> |
        <router-link to="/loans">Loans</router-link> |
        <router-link to="/loans/new">New Loan</router-link>
      </nav>
    </header>

    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
// minimal — no script logic needed for now
</script>

<style scoped>
.app-container { font-family: Inter, system-ui, sans-serif; padding: 1rem; }
.header { display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; }
.header nav a { margin: 0 0.5rem; color: #2c3e50; text-decoration: none; }
.main { background: #fff; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
</style>
