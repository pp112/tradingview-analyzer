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