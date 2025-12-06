import { useEffect, useRef, useState } from 'react';

const FLIGHT_WS_URL = import.meta.env.VITE_FLIGHT_API_URL?.replace('http', 'ws') || 'ws://localhost:8002';

interface PriceUpdateMessage {
  type: 'price_update' | 'subscribed' | 'unsubscribed';
  listing_type?: string;
  listing_id?: string;
  new_price?: number;
  old_price?: number;
  timestamp?: string;
}

export const usePriceUpdates = (flightIds: string[]) => {
  const [priceUpdates, setPriceUpdates] = useState<Map<string, number>>(new Map());
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (flightIds.length === 0) return;

    const connect = () => {
      try {
        const ws = new WebSocket(`${FLIGHT_WS_URL}/ws/price-updates`);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log('WebSocket connected for price updates');
          // Subscribe to all flight IDs
          flightIds.forEach(flightId => {
            ws.send(JSON.stringify({
              action: 'subscribe',
              listing_id: flightId,
              listing_type: 'flight'
            }));
          });
        };

        ws.onmessage = (event) => {
          try {
            const message: PriceUpdateMessage = JSON.parse(event.data);
            
            if (message.type === 'price_update' && message.listing_id && message.new_price !== undefined) {
              console.log(`Price update received for ${message.listing_id}: $${message.old_price} -> $${message.new_price}`);
              setPriceUpdates(prev => {
                const newMap = new Map(prev);
                newMap.set(message.listing_id!, message.new_price!);
                return newMap;
              });
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected, attempting to reconnect...');
          // Reconnect after 3 seconds
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 3000);
        };
      } catch (error) {
        console.error('Error connecting WebSocket:', error);
      }
    };

    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        // Unsubscribe from all flights
        flightIds.forEach(flightId => {
          wsRef.current?.send(JSON.stringify({
            action: 'unsubscribe',
            listing_id: flightId,
            listing_type: 'flight'
          }));
        });
        wsRef.current.close();
      }
    };
  }, [flightIds.join(',')]); // Reconnect if flight IDs change

  return priceUpdates;
};

