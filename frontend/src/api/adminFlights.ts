/**
 * Admin Flight Management API functions
 */

// Always use proxy URLs - Vite dev server will route them correctly
const ADMIN_API_BASE_URL = '/api/admin';

export interface FlightCreateData {
  flight_id: string;
  airline_name: string;
  operator_name?: string;
  departure_airport: string;
  arrival_airport: string;
  departure_datetime: string;
  arrival_datetime: string;
  flight_class: 'economy' | 'business' | 'first';
  base_price: number;
  total_seats: number;
  available_seats?: number;
}

export interface FlightUpdateData {
  airline_name?: string;
  operator_name?: string;
  departure_datetime?: string;
  arrival_datetime?: string;
  base_price?: number;
  available_seats?: number;
  is_active?: boolean;
}

export interface FlightResponse {
  flight_id: string;
  airline_name: string;
  operator_name?: string;
  departure_airport: string;
  arrival_airport: string;
  departure_datetime: string;
  arrival_datetime: string;
  duration_minutes: number;
  flight_class: string;
  base_price: string;
  total_seats: number;
  available_seats: number;
  rating: number;
  total_reviews: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Get admin token from localStorage
 * Falls back to regular token for testing
 */
function getAdminToken(): string | null {
  return localStorage.getItem('admin_token') || localStorage.getItem('token');
}

/**
 * Create a new flight
 */
export async function createFlight(data: FlightCreateData): Promise<{ message: string; flight: FlightResponse }> {
  const token = getAdminToken();
  if (!token) {
    throw new Error('Admin authentication required');
  }

  try {
    const response = await fetch(`${ADMIN_API_BASE_URL}/flights`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      const errorMessage = error.detail || error.message || 'Failed to create flight';
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error('Create flight error:', error);
    throw error;
  }
}

/**
 * Update a flight
 */
export async function updateFlight(
  flightId: string,
  data: FlightUpdateData
): Promise<{ message: string; flight: FlightResponse }> {
  const token = getAdminToken();
  if (!token) {
    throw new Error('Admin authentication required');
  }

  try {
    const response = await fetch(`${ADMIN_API_BASE_URL}/flights/${flightId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      const errorMessage = error.detail || error.message || 'Failed to update flight';
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error('Update flight error:', error);
    throw error;
  }
}

/**
 * Delete a flight
 */
export async function deleteFlight(flightId: string): Promise<{ message: string }> {
  const token = getAdminToken();
  if (!token) {
    throw new Error('Admin authentication required');
  }

  try {
    const response = await fetch(`${ADMIN_API_BASE_URL}/flights/${flightId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      const errorMessage = error.detail || error.message || 'Failed to delete flight';
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error('Delete flight error:', error);
    throw error;
  }
}

/**
 * Get all flights (via flight service search with no filters)
 */
export async function getAllFlights(): Promise<FlightResponse[]> {
  const token = getAdminToken();
  if (!token) throw new Error("Admin authentication required");

  try {
    const response = await fetch(`${ADMIN_API_BASE_URL}/flights`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
    });

    if (!response.ok) {
      const err = await response.json();
      const errorMessage = err.detail || err.message || 'Failed to fetch admin flights';
      throw new Error(errorMessage);
    }

    const data = await response.json();
    return data.flights || [];
  } catch (error: any) {
    console.error("Admin getAllFlights error:", error);
    throw error;
  }
}
