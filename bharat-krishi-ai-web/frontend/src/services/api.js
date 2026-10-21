
import axios from "axios";

// Configure the backend origin in Vercel:
// VITE_API_BASE_URL=https://bharat-krishi-ai.onrender.com

const API_ORIGIN = (
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000"
).replace(/\/+$/, "");

// Add /api exactly once.
// Final production API example:
// https://bharat-krishi-ai.onrender.com/api/auth/register
const API = axios.create({
  baseURL: `${API_ORIGIN}/api`,
  timeout: 30000,
  headers: {
    Accept: "application/json",
  },
});

// Convert registration form fields to the fields expected by
// backend/app/schemas/auth_schema.py.
export const authAPI = {
  register: (form = {}) => {
    const firstName = form.firstName ?? form.first_name ?? "";
    const lastName = form.lastName ?? form.last_name ?? "";

    const phone = String(
      form.phone ??
        form.mobileNumber ??
        form.mobile ??
        form.mobile_number ??
        ""
    ).trim();

    const email = String(form.email ?? "").trim();

    const username = String(
      form.username || email || phone
    ).trim();

    const fullName = String(
      form.name || `${firstName} ${lastName}`.trim()
    ).trim();

    if (!username) {
      return Promise.reject(
        new Error("Enter an email address or mobile number.")
      );
    }

    if (!form.password) {
      return Promise.reject(
        new Error("Enter a password.")
      );
    }

    return API.post("/auth/register", {
      username,
      password: form.password,
      name: fullName || username,
      phone,
      state: form.state || "Telangana",
    });
  },

  login: (form = {}) => {
    const username = String(
      form.username ||
        form.email ||
        form.phone ||
        form.mobileNumber ||
        ""
    ).trim();

    return API.post("/auth/login", {
      username,
      password: form.password,
    });
  },

  me: (token) =>
    API.get("/auth/me", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }),

  updateProfile: (data, token) =>
    API.post("/auth/profile/update", data, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }),
};

// Keep the existing API exports so other project features continue to work.
export const cropAPI = {
  predict: (data) => API.post("/crop/predict", data),
};

export const diseaseAPI = {
  detect: (formData) =>
    API.post("/disease/predict", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }),
};

export const soilAPI = {
  predict: (data) => API.post("/soil/predict", data),
};

export const yieldAPI = {
  predict: (data) => API.post("/yield/predict", data),
};

export const marketAPI = {
  predict: (data) => API.post("/market/predict", data),
};

export const weatherAPI = {
  predict: (data) => API.post("/weather/predict", data),
};

export const schemesAPI = {
  search: (data) => API.post("/schemes/predict", data),
};

export default API;
