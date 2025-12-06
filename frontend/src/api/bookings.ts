/**
 * Booking API service
 */

// Use proxy URL - Vite dev server will route it correctly
const BOOKING_API_BASE_URL = '/api/booking';

export interface BookingCreate {
  user_id: string;
  booking_type: 'flight' | 'hotel' | 'car';
  listing_id: string;
  check_in_date: string; // ISO datetime string
  check_out_date?: string; // ISO datetime string (optional for flights)
  num_passengers?: number;
  flight_class?: string;
  num_rooms?: number;
  room_type?: string;
}

export interface BookingResponse {
  booking_id: string;
  user_id: string;
  booking_type: string;
  listing_id: string;
  check_in_date: string;
  check_out_date?: string;
  num_passengers: number;
  num_rooms: number;
  num_nights: number;
  status: string;
  total_price: number;
  booking_date: string;
  created_at: string;
  updated_at: string;
  listing_details?: any;
  // Billing information (if payment completed)
  subtotal?: number;
  tax_amount?: number;
  total_amount?: number;  // Total with tax
  invoice_number?: string;
}

/**
 * Create a new booking
 */
export async function createBooking(booking: BookingCreate, token: string): Promise<BookingResponse> {
  const url = `${BOOKING_API_BASE_URL}/bookings`;
  console.log('Creating booking:', { url, booking: { ...booking, check_in_date: booking.check_in_date?.substring(0, 20) + '...' } });
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(booking),
    });

    console.log('Booking response status:', response.status, response.statusText);

    if (!response.ok) {
      let errorMessage = 'Failed to create booking';
      try {
        const error = await response.json();
        console.error('Booking error response:', error);
        errorMessage = error.detail?.message || error.detail || error.message || errorMessage;
        // Handle Pydantic validation errors
        if (error.detail && Array.isArray(error.detail)) {
          const validationErrors = error.detail.map((e: any) => {
            const loc = e.loc ? e.loc.join('.') : '';
            return `${loc}: ${e.msg || e.message}`;
          }).join(', ');
          errorMessage = validationErrors || errorMessage;
        }
      } catch (e) {
        // If response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    const result = await response.json();
    console.log('Booking created successfully:', result.booking_id);
    return result;
  } catch (error: any) {
    console.error('Create booking error:', error);
    console.error('Error type:', error?.constructor?.name);
    console.error('Error message:', error?.message);
    
    // Handle network errors (fetch failures)
    if (error instanceof TypeError) {
      if (error.message.includes('fetch') || error.message.includes('Failed to fetch')) {
        throw new Error(`Network error: Could not connect to booking service at ${url}. Please check if the service is running.`);
      }
      throw new Error(`Network error: ${error.message}`);
    }
    
    // Re-throw with original message if it's already an Error
    if (error instanceof Error) {
      throw error;
    }
    
    // Otherwise wrap in Error
    throw new Error(error?.message || 'Failed to create booking. Please try again.');
  }
}

/**
 * Get user's bookings
 */
export async function getUserBookings(
  user_id: string,
  token: string,
  booking_type?: string,
  status?: string
): Promise<BookingResponse[]> {
  try {
    const params = new URLSearchParams();
    if (booking_type) params.append('booking_type', booking_type);
    if (status) params.append('status', status);

    const response = await fetch(
      `${BOOKING_API_BASE_URL}/bookings/user/${user_id}?${params.toString()}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get bookings');
    }

    const data = await response.json();
    // Backend returns BookingListResponse with { bookings: [...], total_count, page, page_size }
    return data.bookings || [];
  } catch (error) {
    console.error('Get bookings error:', error);
    throw error;
  }
}

/**
 * Cancel a booking
 */
export async function cancelBooking(
  booking_id: string,
  token: string,
  reason?: string,
  refund_requested: boolean = false
): Promise<void> {
  const url = `${BOOKING_API_BASE_URL}/bookings/${booking_id}/cancel`;
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ 
        reason: reason || 'Cancelled by user',
        refund_requested 
      }),
    });

    if (!response.ok) {
      let errorMessage = 'Failed to cancel booking';
      try {
        const error = await response.json();
        errorMessage = error.detail || error.message || errorMessage;
      } catch (e) {
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }
  } catch (error: any) {
    console.error('Cancel booking error:', error);
    
    // Handle network errors (fetch failures)
    if (error instanceof TypeError) {
      if (error.message.includes('fetch') || error.message.includes('Failed to fetch')) {
        throw new Error(`Network error: Could not connect to booking service at ${url}. Please check if the service is running.`);
      }
      throw new Error(`Network error: ${error.message}`);
    }
    
    // Re-throw with original message if it's already an Error
    if (error instanceof Error) {
      throw error;
    }
    
    // Otherwise wrap in Error
    throw new Error(error?.message || 'Failed to cancel booking. Please try again.');
  }
}

