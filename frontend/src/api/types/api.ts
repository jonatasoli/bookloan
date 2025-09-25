export interface BookLoan {
  id: number
  book: number
  user: number
  loan_date: string
  due_date: string
  return_date?: string
  status: 'active' | 'returned' | 'overdue'
}

export interface Book {
  id: number
  title: string
  author: string
  isbn: string
  available: boolean
}

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
}

export interface ApiResponse<T = any> {
  data: T
  status: number
  statusText: string
  headers: any
  config: any
}
