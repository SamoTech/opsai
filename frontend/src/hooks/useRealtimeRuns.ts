'use client';
import { useEffect, useRef, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';

const WS_URL = process.env.NEXT_PUBLIC_API_URL?.replace('http', 'ws') || 'ws://localhost:8000';

export function useRealtimeRuns(projectId: string) {
  const queryClient = useQueryClient();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    if (!projectId) return;

    const ws = new WebSocket(`${WS_URL}/api/v1/ws/projects/${projectId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[OpsAI WS] Connected to project', projectId);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'analysis_complete') {
          // Invalidate queries to trigger refetch
          queryClient.invalidateQueries({ queryKey: ['recent-runs'] });
          queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
          queryClient.invalidateQueries({ queryKey: ['runs', projectId] });

          // Show browser notification if permitted
          if (typeof window !== 'undefined' && Notification.permission === 'granted') {
            new Notification('OpsAI — Analysis Complete', {
              body: `Root cause: ${msg.root_cause} (${Math.round(msg.confidence * 100)}% confidence)`,
              icon: '/favicon.ico',
            });
          }
        }
      } catch (e) {
        // ignore parse errors
      }
    };

    ws.onclose = () => {
      console.log('[OpsAI WS] Disconnected. Reconnecting in 5s...');
      reconnectRef.current = setTimeout(connect, 5000);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [projectId, queryClient]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectRef.current);
      wsRef.current?.close();
    };
  }, [connect]);
}
