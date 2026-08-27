/**
 * Bayzid — minimal API client wrapping fetch() against the Django backend.
 * Handles JWT access/refresh tokens stored in localStorage, and consistent
 * error handling for all pages.
 */
const API_BASE_URL = window.BAYZID_API_BASE_URL || "http://localhost:8000/api/v1";

const TokenStore = {
  getAccess: () => localStorage.getItem("bayzid_access"),
  getRefresh: () => localStorage.getItem("bayzid_refresh"),
  set: (access, refresh) => {
    localStorage.setItem("bayzid_access", access);
    if (refresh) localStorage.setItem("bayzid_refresh", refresh);
  },
  clear: () => {
    localStorage.removeItem("bayzid_access");
    localStorage.removeItem("bayzid_refresh");
  },
};

async function apiRequest(path, { method = "GET", body, auth = true, headers = {} } = {}) {
  const finalHeaders = { "Content-Type": "application/json", ...headers };
  if (auth && TokenStore.getAccess()) {
    finalHeaders.Authorization = `Bearer ${TokenStore.getAccess()}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: finalHeaders,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (response.status === 401 && auth && TokenStore.getRefresh()) {
    const refreshed = await refreshAccessToken();
    if (refreshed) return apiRequest(path, { method, body, auth, headers });
  }

  let data = null;
  try {
    data = await response.json();
  } catch (_) {
    /* no JSON body */
  }

  if (!response.ok) {
    const message = data?.detail || Object.values(data || {})[0] || "Something went wrong. Please try again.";
    throw new Error(Array.isArray(message) ? message[0] : message);
  }
  return data;
}

async function refreshAccessToken() {
  try {
    const res = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: TokenStore.getRefresh() }),
    });
    if (!res.ok) throw new Error("refresh failed");
    const data = await res.json();
    TokenStore.set(data.access);
    return true;
  } catch (_) {
    TokenStore.clear();
    return false;
  }
}

const BayzidAPI = {
  register: (payload) => apiRequest("/auth/register/", { method: "POST", body: payload, auth: false }),
  login: (payload) => apiRequest("/auth/login/", { method: "POST", body: payload, auth: false }),
  requestOtp: (payload) => apiRequest("/auth/otp/request/", { method: "POST", body: payload, auth: false }),
  verifyOtp: (payload) => apiRequest("/auth/otp/verify/", { method: "POST", body: payload, auth: false }),
  resetPassword: (payload) => apiRequest("/auth/password-reset/confirm/", { method: "POST", body: payload, auth: false }),
  me: () => apiRequest("/auth/me/"),
  products: (query = "") => apiRequest(`/products/${query}`, { auth: false }),
  categories: () => apiRequest("/products/categories/", { auth: false }),
};

window.TokenStore = TokenStore;
window.BayzidAPI = BayzidAPI;
