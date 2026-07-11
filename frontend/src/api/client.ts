import axios from "axios";

import { env } from "@/config/env";

import { parseApiError } from "./errors";

/**
 * Central HTTP client. All backend communication must go through this layer.
 * Real API modules (cameras, events, etc.) will be added in future phases.
 */
export const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
  timeout: 30_000,
});

apiClient.interceptors.request.use((config) => {
  // Auth token attachment will be added when authentication is implemented.
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(parseApiError(error)),
);

export type ApiClient = typeof apiClient;
