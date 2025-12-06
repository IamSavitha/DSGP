/**
 * Bundles API functions for AI Recommendation Service
 */

const AI_API_BASE_URL = '/api/ai';

export interface BundleRequest {
  origin?: string;
  destination: string;
  departure_date: string;
  return_date?: string;
  budget?: number;
  num_travelers: number;
  preferences?: Record<string, any>;
}

export interface FlightInfo {
  id: string;
  airline: string;
  route: string;
  price: number;
  departure_datetime?: string;
  duration_minutes: number;
  available_seats: number;
}

export interface HotelInfo {
  id: string;
  name: string;
  city: string;
  price_per_night: number;
  total_price: number;
  stars: number;
  amenities: string;
}

export interface CarInfo {
  id: string;
  make: string;
  model: string;
  car_type: string;
  provider: string;
  daily_price: number;
  total_price: number;
  seats: number;
  location: string;
}

export interface Bundle {
  bundle_id: string;
  flight: FlightInfo;
  hotel: HotelInfo;
  car: CarInfo;
  total_price: number;
  fit_score: number;
  explanation: string;
  num_nights: number;
  num_travelers: number;
}

export interface BundleResponse {
  bundles: Bundle[];
  total_found: number;
  query_params: BundleRequest;
}

/**
 * Find trip bundles (Flight + Hotel + Car)
 */
export async function findBundles(request: BundleRequest): Promise<BundleResponse> {
  try {
    const response = await fetch(`${AI_API_BASE_URL}/bundles`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Failed to find bundles' }));
      throw new Error(error.detail || error.message || 'Failed to find bundles');
    }

    return await response.json();
  } catch (error: any) {
    console.error('Find bundles error:', error);
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error(`Network error: Could not connect to AI service at ${AI_API_BASE_URL}. Please check if the service is running.`);
    }
    throw error;
  }
}

