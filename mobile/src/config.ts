const DEFAULT_API_BASE_URL = "http://localhost:8000";

/**
 * Expo replaces EXPO_PUBLIC_* variables at build time. The fallback keeps
 * local development and automated tests working without an .env file.
 */
export const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL?.trim() || DEFAULT_API_BASE_URL;
