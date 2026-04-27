import { useQuery } from '@tanstack/react-query';
import {
  getCapabilities,
  getHealth,
  listVoices,
  analyzeText,
  validateSsml,
  listVoiceCharacters,
  type VoiceCharacterQuery,
} from '@/api/endpoints';

export const queryKeys = {
  health: ['health'] as const,
  capabilities: ['capabilities'] as const,
  voices: ['voices'] as const,
  voice: (id: string) => ['voices', id] as const,
  voiceCharacters: (q: VoiceCharacterQuery) => ['voice-characters', q] as const,
  analysis: (text: string) => ['analyze', text] as const,
  ssmlValidation: (ssml: string) => ['ssml-validate', ssml] as const,
};

export function useHealthQuery(intervalMs = 15_000) {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: getHealth,
    refetchInterval: (query) => {
      if (typeof navigator !== 'undefined' && !navigator.onLine) return false;
      const status = (query.state.data as { status?: string } | undefined)?.status;
      // Back off when backend is down to reduce noisy retry traffic.
      return status === 'down' ? Math.max(intervalMs, 60_000) : intervalMs;
    },
    retry: false,
    staleTime: intervalMs / 2,
    gcTime: intervalMs,
  });
}

export function useCapabilitiesQuery() {
  return useQuery({
    queryKey: queryKeys.capabilities,
    queryFn: getCapabilities,
    networkMode: 'offlineFirst',
    staleTime: 5 * 60_000,
  });
}

export function useVoicesQuery() {
  return useQuery({
    queryKey: queryKeys.voices,
    queryFn: listVoices,
    networkMode: 'offlineFirst',
    staleTime: 15 * 60_000,
  });
}

export function useVoiceCharactersQuery(query: VoiceCharacterQuery, enabled = true) {
  return useQuery({
    queryKey: queryKeys.voiceCharacters(query),
    queryFn: () => listVoiceCharacters(query),
    enabled,
    staleTime: 60_000,
    placeholderData: (previous) => previous,
  });
}

export function useAnalyzeQuery(text: string, enabled = true) {
  return useQuery({
    queryKey: queryKeys.analysis(text),
    queryFn: () => analyzeText(text),
    enabled: enabled && text.trim().length > 0,
    staleTime: 60_000,
  });
}

export function useSsmlValidateQuery(ssml: string, enabled = true) {
  return useQuery({
    queryKey: queryKeys.ssmlValidation(ssml),
    queryFn: () => validateSsml(ssml),
    enabled: enabled && ssml.trim().length > 0,
    staleTime: 30_000,
  });
}
