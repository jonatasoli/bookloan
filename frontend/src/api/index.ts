/**
 * Axios wrapper for the frontend.
 * - Use `import type` for type-only imports because `verbatimModuleSyntax` is enabled.
 * - Use InternalAxiosRequestConfig for request interceptor param to match axios internals.
 */

import axios from "axios";
import type {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
  InternalAxiosRequestConfig,
} from "axios";

const API_BASE = (import.meta.env.VITE_API_BASE as string) || "";

/**
 * Create axios instance
 */
const api: AxiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

/**
 * Request interceptor
 * Use InternalAxiosRequestConfig to satisfy axios v1 internal types.
 */
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // ensure headers exist (fixes strict header typing mismatch)
    config.headers = config.headers ?? {};

    // Example: attach auth token from localStorage (adjust to your app)
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    if (token) {
      // axios uses AxiosRequestHeaders shape; this assignment is safe after ensuring headers exists
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore -- some axios header types are strict; runtime assignment is ok
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor
 */
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    // centralize error handling if needed
    // example: if (error.response?.status === 401) { ... }
    return Promise.reject(error);
  }
);

/**
 * Helper typed request function (optional)
 */
export async function request<T = any>(cfg: AxiosRequestConfig): Promise<T> {
  const resp = await api.request<T>(cfg);
  return resp.data;
}

export default api;
