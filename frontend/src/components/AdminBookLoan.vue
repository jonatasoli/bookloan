<template>
  <div class="admin-book-loan">
    <div class="container">
      <div class="page-header">
        <h1>Book Loan Administration</h1>
        <button @click="showCreateModal" class="btn btn-primary">
          <i class="icon-plus"></i>
          New Loan
        </button>
      </div>

      <!-- Statistics -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <h3>Total Loans</h3>
            <p>{{ statistics.totalLoans }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📖</div>
          <div class="stat-content">
            <h3>Active Loans</h3>
            <p>{{ statistics.activeLoans }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⚠️</div>
          <div class="stat-content">
            <h3>Overdue Loans</h3>
            <p>{{ statistics.overdueLoans }}</p>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-section">
        <div class="filters">
          <select v-model="filters.status" @change="fetchLoans" class="form-control">
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="active">Active</option>
            <option value="returned">Returned</option>
            <option value="overdue">Overdue</option>
          </select>

          <input
            type="text"
            v-model="filters.search"
            placeholder="Search by book or user..."
            @input="debouncedSearch"
            class="form-control"
          >

          <button @click="clearFilters" class="btn btn-secondary">
            Clear Filters
          </button>
        </div>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading loans...</p>
      </div>

      <!-- Loans table -->
      <div v-else class="table-section">
        <div class="table-container">
          <table class="loans-table table">
            <thead>
              <tr>
                <th>Book</th>
                <th>User</th>
                <th>Loan Date</th>
                <th>Due Date</th>
                <th>Return Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="loan in loans" :key="loan.id" :class="{ 'overdue-row': isOverdue(loan) }">
                <td class="book-info">
                  <strong>{{ loan.book_details?.title || loan.book_title }}</strong>
                  <small>by {{ loan.book_details?.author }}</small>
                </td>
                <td class="user-info">
                  <strong>{{ loan.student_details?.full_name || loan.student_name }}</strong>
                  <small>{{ loan.student_details?.email }}</small>
                </td>
                <td>{{ formatDate(loan.loan_date) }}</td>
                <td>{{ formatDate(loan.due_date) }}</td>
                <td>{{ loan.return_date ? formatDate(loan.return_date) : '-' }}</td>
                <td>
                  <span :class="`status status-${loan.status}`">
                    {{ getStatusText(loan.status) }}
                  </span>
                  <span v-if="isOverdue(loan)" class="overdue-badge">
                    {{ getDaysOverdue(loan) }} days overdue
                  </span>
                </td>
                <td class="actions">
                  <button
                    v-if="loan.status === 'pending'"
                    @click="approveLoan(loan.id)"
                    class="btn btn-success btn-sm"
                    title="Approve Loan"
                  >
                    Approve
                  </button>
                  <button
                    v-if="loan.status === 'active'"
                    @click="markAsReturned(loan.id)"
                    class="btn btn-primary btn-sm"
                    title="Mark as Returned"
                  >
                    Return
                  </button>
                  <button
                    v-if="loan.status === 'active'"
                    @click="renewLoan(loan.id)"
                    class="btn btn-warning btn-sm"
                    title="Renew Loan"
                  >
                    Renew
                  </button>
                  <button
                    @click="editLoan(loan)"
                    class="btn btn-secondary btn-sm"
                    title="Edit Loan"
                  >
                    Edit
                  </button>
                  <button
                    @click="deleteLoan(loan.id)"
                    class="btn btn-danger btn-sm"
                    title="Delete Loan"
                    v-if="loan.status === 'pending'"
                  >
                    Delete
                  </button>
                </td>
              </tr>
              <tr v-if="loans.length === 0">
                <td colspan="7" class="no-data">
                  No loans found
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="pagination" v-if="totalPages > 1">
          <button
            @click="changePage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="btn btn-secondary"
          >
            Previous
          </button>

          <span class="page-info">
            Page {{ currentPage }} of {{ totalPages }}
          </span>

          <button
            @click="changePage(currentPage + 1)"
            :disabled="currentPage >= totalPages"
            class="btn btn-secondary"
          >
            Next
          </button>
        </div>
      </div>

      <!-- Create/Edit Modal -->
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal" @click.stop>
          <div class="modal-header">
            <h3>{{ editingLoan ? 'Edit Loan' : 'Create New Loan' }}</h3>
            <button @click="closeModal" class="close-btn">&times;</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveLoan">
              <div class="form-group">
                <label>User</label>
                <select v-model="loanForm.user_id" required class="form-control">
                  <option value="">Select User</option>
                  <option v-for="user in users" :key="user.id" :value="user.id">
                    {{ user.full_name || user.username }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label>Book</label>
                <select v-model="loanForm.book_id" required class="form-control">
                  <option value="">Select Book</option>
                  <option v-for="book in availableBooks" :key="book.id" :value="book.id">
                    {{ book.title }} by {{ book.author }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label>Due Date</label>
                <input
                  type="date"
                  v-model="loanForm.due_date"
                  required
                  class="form-control"
                  :min="new Date().toISOString().split('T')[0]"
                >
              </div>

              <div class="form-group">
                <label>Notes (Optional)</label>
                <textarea
                  v-model="loanForm.notes"
                  class="form-control"
                  rows="3"
                  placeholder="Add any additional notes..."
                ></textarea>
              </div>

              <div class="form-actions">
                <button type="button" @click="closeModal" class="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary">
                  {{ editingLoan ? 'Update' : 'Create' }} Loan
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/api'
import { useToast } from 'vue-toastification'

export default {
  name: 'AdminBookLoan',
  setup() {
    const toast = useToast()
    return { toast }
  },
  data() {
    return {
      loans: [],
      users: [],
      availableBooks: [],
      filters: {
        status: '',
        search: ''
      },
      statistics: {
        totalLoans: 0,
        activeLoans: 0,
        overdueLoans: 0
      },
      currentPage: 1,
      pageSize: 10,
      totalPages: 1,
      loading: true,
      showModal: false,
      editingLoan: null,
      loanForm: {
        user_id: '',
        book_id: '',
        due_date: '',
        notes: ''
      },
      searchTimeout: null
    }
  },
  mounted() {
    this.fetchLoans()
    this.fetchStatistics()
    this.fetchUsers()
    this.fetchAvailableBooks()
  },
  methods: {
    async fetchLoans() {
      try {
        this.loading = true
        const params = {
          page: this.currentPage,
          page_size: this.pageSize,
          ...this.filters
        }

        // Remove empty filters
        Object.keys(params).forEach(key => {
          if (!params[key]) delete params[key]
        })

        const response = await api.getLoans(params)
        this.loans = response.data.results || response.data

        // Handle pagination
        if (response.data.count) {
          this.totalPages = Math.ceil(response.data.count / this.pageSize)
        }

      } catch (error) {
        console.error('Error loading loans:', error)
        this.toast.error('Failed to load loans')
      } finally {
        this.loading = false
      }
    },

    async fetchStatistics() {
      try {
        const response = await api.getStatistics()
        this.statistics = response.data
      } catch (error) {
        console.error('Error loading statistics:', error)
      }
    },

    async fetchUsers() {
      try {
        // This would need a users endpoint in your API
        // For now, we'll skip this or you can add it to your Django API
        this.users = []
      } catch (error) {
        console.error('Error loading users:', error)
      }
    },

    async fetchAvailableBooks() {
      try {
        const response = await api.getAvailableBooks()
        this.availableBooks = response.data.results || response.data
      } catch (error) {
        console.error('Error loading books:', error)
      }
    },

    async approveLoan(loanId) {
      try {
        await api.updateLoan(loanId, { status: 'active' })
        this.toast.success('Loan approved successfully')
        this.fetchLoans()
        this.fetchStatistics()
      } catch (error) {
        console.error('Error approving loan:', error)
        this.toast.error('Failed to approve loan')
      }
    },

    async markAsReturned(loanId) {
      try {
        await api.returnBook(loanId)
        this.toast.success('Book marked as returned')
        this.fetchLoans()
        this.fetchStatistics()
      } catch (error) {
        console.error('Error returning book:', error)
        this.toast.error('Failed to return book')
      }
    },

    async renewLoan(loanId) {
      try {
        await api.renewLoan(loanId)
        this.toast.success('Loan renewed successfully')
        this.fetchLoans()
      } catch (error) {
        console.error('Error renewing loan:', error)
        this.toast.error('Failed to renew loan')
      }
    },

    async deleteLoan(loanId) {
      if (!confirm('Are you sure you want to delete this loan?')) return

      try {
        await api.deleteLoan(loanId)
        this.toast.success('Loan deleted successfully')
        this.fetchLoans()
        this.fetchStatistics()
      } catch (error) {
        console.error('Error deleting loan:', error)
        this.toast.error('Failed to delete loan')
      }
    },

    showCreateModal() {
      this.editingLoan = null
      this.resetForm()
      this.showModal = true
    },

    editLoan(loan) {
      this.editingLoan = loan
      this.loanForm = {
        user_id: loan.user?.id || '',
        book_id: loan.book?.id || '',
        due_date: loan.due_date,
        notes: loan.notes || ''
      }
      this.showModal = true
    },

    closeModal() {
      this.showModal = false
      this.editingLoan = null
      this.resetForm()
    },

    resetForm() {
      this.loanForm = {
        user_id: '',
        book_id: '',
        due_date: this.getDefaultDueDate(),
        notes: ''
      }
    },

    async saveLoan() {
      try {
        if (this.editingLoan) {
          await api.updateLoan(this.editingLoan.id, this.loanForm)
          this.toast.success('Loan updated successfully')
        } else {
          await api.createLoan(this.loanForm)
          this.toast.success('Loan created successfully')
        }

        this.closeModal()
        this.fetchLoans()
        this.fetchStatistics()
      } catch (error) {
        console.error('Error saving loan:', error)
        const message = error.response?.data?.message || 'Failed to save loan'
        this.toast.error(message)
      }
    },

    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        this.fetchLoans()
      }
    },

    clearFilters() {
      this.filters = { status: '', search: '' }
      this.currentPage = 1
      this.fetchLoans()
    },

    debouncedSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.currentPage = 1
        this.fetchLoans()
      }, 500)
    },

    formatDate(dateString) {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('en-US')
    },

    getStatusText(status) {
      const statusMap = {
        'pending': 'Pending',
        'active': 'Active',
        'returned': 'Returned',
        'overdue': 'Overdue'
      }
      return statusMap[status] || status
    },

    isOverdue(loan) {
      if (loan.status !== 'active') return false
      return new Date() > new Date(loan.due_date)
    },

    getDaysOverdue(loan) {
      if (!this.isOverdue(loan)) return 0
      const today = new Date()
      const dueDate = new Date(loan.due_date)
      const diffTime = today - dueDate
      return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    },

    getDefaultDueDate() {
      const date = new Date()
      date.setDate(date.getDate() + 14) // Default 2 weeks
      return date.toISOString().split('T')[0]
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0;
  font-size: 2rem;
  color: #333;
}

.icon-plus::before {
  content: "➕";
  margin-right: 5px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  font-size: 2rem;
  opacity: 0.8;
}

.stat-content h3 {
  margin: 0 0 5px 0;
  font-size: 0.9rem;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-content p {
  margin: 0;
  font-size: 1.8rem;
  font-weight: bold;
  color: var(--primary-color);
}

.filters-section {
  background: white;
  padding: 20px;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  margin-bottom: 20px;
}

.filters {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.filters .form-control {
  min-width: 200px;
  flex: 1;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.table-section {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  overflow: hidden;
}

.table-container {
  overflow-x: auto;
}

.loans-table {
  margin-bottom: 0;
}

.loans-table th {
  background-color: var(--light-color);
  font-weight: 600;
  white-space: nowrap;
}

.overdue-row {
  background-color: #fff5f5;
}

.book-info strong,
.user-info strong {
  display: block;
  margin-bottom: 2px;
}

.book-info small,
.user-info small {
  color: #666;
  font-size: 0.85rem;
}

.status {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-pending {
  background-color: #fff3cd;
  color: #856404;
}

.status-active {
  background-color: #d1ecf1;
  color: #0c5460;
}

.status-returned {
  background-color: #d4edda;
  color: #155724;
}

.status-overdue {
  background-color: #f8d7da;
  color: #721c24;
}

.overdue-badge {
  display: block;
  font-size: 0.7rem;
  color: var(--danger-color);
  font-weight: bold;
  margin-top: 2px;
}

.actions {
  white-space: nowrap;
}

.actions .btn {
  margin-right: 5px;
  margin-bottom: 5px;
}

.no-data {
  text-align: center;
  color: #666;
  font-style: italic;
  padding: 40px 20px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border-top: 1px solid #dee2e6;
}

.page-info {
  font-weight: 500;
  color: #666;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #dee2e6;
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #dee2e6;
}

/* Responsive */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters {
    flex-direction: column;
    align-items: stretch;
  }

  .filters .form-control {
    min-width: auto;
  }

  .modal {
    width: 95%;
    margin: 20px;
  }

  .table-container {
    font-size: 0.9rem;
  }

  .actions .btn {
    padding: 0.2rem 0.4rem;
    font-size: 0.8rem;
  }
}
</style>
