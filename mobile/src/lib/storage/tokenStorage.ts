import * as SecureStore from "expo-secure-store";
import { Platform } from "react-native";

const ACCESS_TOKEN_KEY = "qualifil.accessToken";
const REFRESH_TOKEN_KEY = "qualifil.refreshToken";

export interface TokenPair {
  access: string;
  refresh: string;
}

export interface TokenStorage {
  getAccessToken(): Promise<string | null>;
  getRefreshToken(): Promise<string | null>;
  setAccessToken(token: string): Promise<void>;
  setTokens(tokens: TokenPair): Promise<void>;
  clear(): Promise<void>;
}

/**
 * Non-persistent storage used on web and in tests. The browser client uses
 * the httpOnly-cookie flow instead of localStorage.
 */
export function createMemoryTokenStorage(
  initialToken: string | null = null,
  initialRefreshToken: string | null = null,
): TokenStorage {
  let accessToken = initialToken;
  let refreshToken = initialRefreshToken;

  return {
    async getAccessToken() {
      return accessToken;
    },
    async getRefreshToken() {
      return refreshToken;
    },
    async setAccessToken(nextToken) {
      accessToken = nextToken;
    },
    async setTokens(tokens) {
      accessToken = tokens.access;
      refreshToken = tokens.refresh;
    },
    async clear() {
      accessToken = null;
      refreshToken = null;
    },
  };
}

/** Persistent storage backed by the platform keychain/keystore. */
export function createSecureTokenStorage(): TokenStorage {
  return {
    async getAccessToken() {
      return SecureStore.getItemAsync(ACCESS_TOKEN_KEY);
    },
    async getRefreshToken() {
      return SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
    },
    async setAccessToken(token) {
      await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, token);
    },
    async setTokens(tokens) {
      await SecureStore.setItemAsync(ACCESS_TOKEN_KEY, tokens.access);
      await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, tokens.refresh);
    },
    async clear() {
      await SecureStore.deleteItemAsync(ACCESS_TOKEN_KEY);
      await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
    },
  };
}

export function createTokenStorage(): TokenStorage {
  return Platform.OS === "web" ? createMemoryTokenStorage() : createSecureTokenStorage();
}

export const tokenStorage = createTokenStorage();
