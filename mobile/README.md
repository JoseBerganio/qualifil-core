# QUALIFIL Mobile

React Native application built with Expo (SDK 58) and TypeScript.

## Structure

- `src/app/` — navigation shell
- `src/screens/` — screens
- `src/components/` — reusable presentational components
- `src/lib/api/` — API access through the shared `@qualifil/api-client`
- `src/lib/i18n/` — English, Filipino, and Hiligaynon localization
- `src/lib/storage/` — secure token storage abstraction
- `src/theme.ts` — shared design tokens

## Setup

Run installs from the repository root so the npm workspace links the shared
client:

```sh
npm install
```

Copy `mobile/.env.example` to `mobile/.env` and set a reachable backend origin.
For a physical device use your computer's LAN IP (for example
`http://192.168.1.10:8000`); `localhost` only works in a simulator on the same
machine.

## Commands

```sh
npm run start -w qualifil-mobile     # Expo start
npm run web -w qualifil-mobile       # Expo web
npm run lint -w qualifil-mobile
npm run typecheck -w qualifil-mobile
npm test -w qualifil-mobile
```

## Notes

- The API base URL comes from `EXPO_PUBLIC_API_BASE_URL`.
- `tsconfig.json` mirrors the Expo SDK 58 base compiler options inline instead of
  extending `expo/tsconfig.base`. This keeps editor/TypeScript 7 resolution
  working in the npm workspace; update it if the Expo base config changes.
- Test files import Jest globals from `@jest/globals` so no global type packages
  are required.
- Access tokens are abstracted behind `TokenStorage`. Native builds use
  `expo-secure-store`; web falls back to in-memory storage until the v0.2.0
  authentication work introduces an httpOnly-cookie flow.
- Sprint 01E only implements the foundation and the backend connectivity screen.
