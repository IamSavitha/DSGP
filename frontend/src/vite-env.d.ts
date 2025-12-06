/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_FLIGHT_API_URL?: string;
  readonly VITE_HOTEL_API_URL?: string;
  readonly VITE_CAR_API_URL?: string;
  readonly VITE_SEARCH_API_URL?: string;
  readonly VITE_BOOKING_API_URL?: string;
  readonly VITE_ADMIN_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

