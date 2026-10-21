import axios from "axios";

const API_ORIGIN = (
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000"
).replace(/\/+$/, "");

const API = axios.create({
  baseURL: `${API_ORIGIN}/api`,
  timeout: 30000,
  headers: {
    Accept: "application/json",
  },
});

// Authentication endpoints
export const authAPI = {
  register: (form = {}) => {
    const firstName = form.firstName || form.first_name || "";
    const lastName = form.lastName || form.last_name || "";

    const phone = String(
      form.phone ||
      form.mobileNumber ||
      form.mobile_number ||
      form.mobile ||
      ""
    ).trim();

    const email = String(form.email || "").trim();
    const username = String(form.username || email || phone).trim();

    const name = String(
      form.name || `${firstName} ${lastName}`.trim()
    ).trim();

    if (!username) {
      throw new Error("Enter a mobile number or email address.");
    }

    if (!form.password) {
      throw new Error("Enter a password.");
    }

    return API.post("/auth/register", {
      username,
      password: form.password,
      name: name || username,
      phone,
      state: form.state || "Telangana",
    });
  },

  login: (form = {}) =>
    API.post("/auth/login", {
      username: String(
        form.username ||
        form.email ||
        form.phone ||
        form.mobileNumber ||
        ""
      ).trim(),
      password: form.password,
    }),

  me: (token) =>
    API.get("/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    }),

  history: (token) =>
    API.get("/auth/history", {
      headers: { Authorization: `Bearer ${token}` },
    }),
};

// Preserve existing exports used by the other application modules.
export const cropAPI = {
  predict: (data) => API.post("/crop/predict", data),
};

export const diseaseAPI = {
  detect: (formData) =>
    API.post("/disease/predict", formData, {
      headers: { "Content-Type": "multipart/form-data" },
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
