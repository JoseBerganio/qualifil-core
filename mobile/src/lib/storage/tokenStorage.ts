import * as SecureStore from "expo-secure-store";
import { Platform } from "react-native";

const ACCESS_TOKEN_KEY = "qualifil.accessToken";

export interface TokenStorage {
  getAccessToken(): Promise<string | null>;
  setAccessToken(token: string): Promise<void>;
  clear(): Promise<void>;
}

/**
 * Non-persistent storage used on web and in tests. Authentication in v0.2.0
 * will use an httpOnly-cookie flow for web instead of localStorage.
 */
export function createMemoryTokenStorage(initialToken: string | null = null): TokenStorage {
  let token = initialToken;

  return {
    async getAccessToken() {
      return token;
    },
    async setAccessToken(nextToken) {
      token = nextToken;
    },
    async clear() {
      token = null;
    },
  };
}

/** Persistent storage backed by the platform keychain/keystore. */
export function createSecureTokenStorage(): TokenStorage {
  return {
    async getAccessToken() {
      return SecureStore.getItemAsync(ACCESS_TOKEN_KEY);
    },
    async setAccessToken(token) {
      await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, token);
    },
    async clear() {
      await SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY);
    },
  };
}

export function createTokenStorage(): TokenStorage {
  return Platform.OS === "web" ? createMemoryTokenStorage() : createSecureTokenStorage();
}

export const tokenStorage = createTokenStorage();
