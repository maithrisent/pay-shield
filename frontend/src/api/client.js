import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const client = axios.create({
  baseURL: API_BASE_URL,
});

// Every outgoing request automatically carries the token, if one exists —
// so individual pages never need to attach the Authorization header themselves.
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("payshield_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default client;