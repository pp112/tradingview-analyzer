export const API_BASE_URL = "http://localhost:8000";

export class ApiError extends Error {
  public status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`);

  if (!res.ok) {
    throw new ApiError(`Ошибка запроса ${path}: ${res.status}`, res.status);
  }

  return res.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    throw new ApiError(`Ошибка запроса ${path}: ${res.status}`, res.status);
  }

  return res.json() as Promise<T>;
}

export async function apiDelete<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    throw new ApiError(`Ошибка запроса ${path}: ${res.status}`, res.status);
  }

  return res.json() as Promise<T>;
}
