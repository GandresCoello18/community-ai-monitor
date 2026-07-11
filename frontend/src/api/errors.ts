import axios, { type AxiosError } from "axios";

import type { ApiErrorBody } from "@/types";

export class ApiError extends Error {
  readonly code: string;
  readonly status?: number;

  constructor(code: string, message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
  }
}

export function parseApiError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiErrorBody>;
    const body = axiosError.response?.data;

    if (body?.error) {
      return new ApiError(
        body.error.code,
        body.error.message,
        axiosError.response?.status,
      );
    }

    if (axiosError.code === "ERR_NETWORK") {
      return new ApiError(
        "NETWORK_ERROR",
        "No fue posible conectar con el servidor.",
      );
    }

    return new ApiError(
      "UNKNOWN_ERROR",
      axiosError.message || "Ocurrió un error inesperado.",
      axiosError.response?.status,
    );
  }

  if (error instanceof ApiError) {
    return error;
  }

  return new ApiError("UNKNOWN_ERROR", "Ocurrió un error inesperado.");
}
