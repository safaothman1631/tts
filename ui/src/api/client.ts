import type { AxiosError} from 'axios';
import axios, { type AxiosInstance } from 'axios';
import { config } from '@/lib/config';
import { get as idbGet } from 'idb-keyval';
import type { ApiError } from '@/types/api';

let _client: AxiosInstance | null = null;

function buildClient(): AxiosInstance {
  const instance = axios.create({
    baseURL: config.apiBaseUrl,
    timeout: 60_000,
    headers: { Accept: 'application/json' },
  });

  instance.interceptors.request.use(async (cfg) => {
    try {
      const token = await idbGet<string>(config.storage.apiToken);
      if (token) {
        cfg.headers.set('Authorization', `Bearer ${token}`);
      }
    } catch {
      /* token store unavailable */
    }
    return cfg;
  });

  instance.interceptors.response.use(
    (r) => r,
    (err: AxiosError) => {
      const apiErr: ApiError = {
        status: err.response?.status ?? 0,
        message:
          (err.response?.data as { message?: string; detail?: string })?.message ||
          (err.response?.data as { detail?: string })?.detail ||
          err.message ||
          'Request failed',
        detail: err.response?.data,
      };
      return Promise.reject(apiErr);
    },
  );

  return instance;
}

export function apiClient(): AxiosInstance {
  if (!_client) _client = buildClient();
  return _client;
}
