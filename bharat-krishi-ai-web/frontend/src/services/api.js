import axios from "axios";

const API_ORIGIN = (
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV
    ? "http://127.0.0.1:8000"
    : "https://bharat-krishi-ai.onrender.com")
).replace(/\/+$/, "");

const API = axios.create({
  baseURL: `${API_ORIGIN}/api`,
  timeout: 30000,
  headers: {
    Accept: "application/json",
  },
});

// Authentication
export const authAPI = {
  register: (payload) => API.post("/auth/register", payload),

  login: (payload) => API.post("/auth/login", payload),

  me: (token) =>
    API.get("/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    }),

  history: (token) =>
    API.get("/auth/history", {
      headers: { Authorization: `Bearer ${token}` },
    }),

  updateProfile: (payload, token) =>
    API.post("/auth/profile/update", payload, {
      headers: { Authorization: `Bearer ${token}` },
    }),
};

// Crop recommendation
export const cropAPI = {
  predict: (data) => API.post("/crop/predict", data),
};

// Plant disease detection
export const diseaseAPI = {
  detect: (formData) =>
    API.post("/disease/predict", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
};

// Soil analysis
export const soilAPI = {
  predict: (data) => API.post("/soil/predict", data),
};

// Crop yield
export const yieldAPI = {
  predict: (data) => API.post("/yield/predict", data),
};

// Market prices
export const marketAPI = {
  predict: (data) => API.post("/market/predict", data),
};

// Weather
export const weatherAPI = {
  predict: (data) => API.post("/weather/predict", data),
};

// Government schemes
export const schemesAPI = {
  search: (data) => API.post("/schemes/predict", data),
};

// Crop rotation
export const rotationAPI = {
  predict: (data) => API.post("/rotation/predict", data),
};

export default API;
