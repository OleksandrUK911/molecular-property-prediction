// API client, matching ../backend-spec/api-contract.md.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new ApiError("Server unavailable, please try again", 0);
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(body.detail || "Server unavailable, please try again", response.status);
  }
  return response.json();
}

export function predict(smiles) {
  return request("/predict", { method: "POST", body: JSON.stringify({ smiles }) });
}

export function getModelInfo() {
  return request("/model/info");
}

export function getHealth() {
  return request("/health");
}

export function getHistory() {
  return request("/history");
}
