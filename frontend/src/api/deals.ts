/**
 * Deals API functions for AI Recommendation Service
 */

const AI_API_BASE_URL = '/api/ai';

export interface Deal {
  listing_id: string;
  listing_type: 'flight' | 'hotel' | 'car';
  current_price: number;
  avg_price: number;
  discount_pct: number;
  deal_score: number;
  tags: string[];
}

export interface DealFilters {
  listing_type?: 'flight' | 'hotel' | 'car';
  min_score?: number;
  limit?: number;
}

/**
 * Get current deals from the AI service
 */
export async function getDeals(filters?: DealFilters): Promise<Deal[]> {
  try {
    const params = new URLSearchParams();
    
    if (filters?.listing_type) {
      params.append('listing_type', filters.listing_type);
    }
    if (filters?.min_score !== undefined && filters.min_score > 0) {
      params.append('min_score', filters.min_score.toString());
    }
    if (filters?.limit) {
      params.append('limit', filters.limit.toString());
    }

    const url = `${AI_API_BASE_URL}/deals${params.toString() ? `?${params.toString()}` : ''}`;
    const response = await fetch(url);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to fetch deals' }));
      throw new Error(error.detail || error.message || 'Failed to fetch deals');
    }

    return await response.json();
  } catch (error: any) {
    console.error('Get deals error:', error);
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error(`Network error: Could not connect to AI service at ${AI_API_BASE_URL}. Please check if the service is running.`);
    }
    throw error;
  }
}

