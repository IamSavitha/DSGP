/**
 * Admin Bookings API service
 */

const ADMIN_API_BASE_URL = '/api/admin';

export interface AdminBooking {
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
  booking_date?: string;
  created_at: string;
  updated_at: string;
}

export interface AdminBookingListResponse {
  bookings: AdminBooking[];
  total: number;
  page: number;
  page_size: number;
}

export interface DashboardStats {
  total_users: number;
  total_revenue: number;
  total_bookings: number;
  active_listings: number;
}

/**
 * Get all bookings (admin only)
 */
export async function getAllBookings(
  token: string,
  page: number = 1,
  pageSize: number = 20,
  bookingType?: string,
  status?: string
): Promise<AdminBookingListResponse> {
  try {
    const params = new URLSearchParams();
    params.append('page', page.toString());
    params.append('page_size', pageSize.toString());
    if (bookingType) params.append('booking_type', bookingType);
    if (status) params.append('status', status);

    const response = await fetch(`${ADMIN_API_BASE_URL}/bookings?${params.toString()}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get bookings');
    }

    return await response.json();
  } catch (error: any) {
    console.error('Get bookings error:', error);
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Network error: Could not connect to admin service');
    }
    throw error;
  }
}

/**
 * Get dashboard statistics (admin only)
 */
export async function getDashboardStats(token: string): Promise<DashboardStats> {
  try {
    const response = await fetch(`${ADMIN_API_BASE_URL}/dashboard/stats`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get dashboard stats');
    }

    return await response.json();
  } catch (error: any) {
    console.error('Get dashboard stats error:', error);
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Network error: Could not connect to admin service');
    }
    throw error;
  }
}

/**
 * Update booking status (admin only)
 */
export async function updateBookingStatus(
  bookingId: string,
  status: string,
  token: string
): Promise<void> {
  try {
    const response = await fetch(`${ADMIN_API_BASE_URL}/bookings/${bookingId}/status`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ status }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update booking status');
    }
  } catch (error: any) {
    console.error('Update booking status error:', error);
    throw error;
  }
}

/**
 * Cancel booking as admin (admin only)
 */
export async function adminCancelBooking(
  bookingId: string,
  reason: string,
  refundRequested: boolean,
  token: string
): Promise<any> {
  try {
    const response = await fetch(`${ADMIN_API_BASE_URL}/bookings/${bookingId}/cancel`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ reason, refund_requested: refundRequested }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to cancel booking');
    }

    return await response.json();
  } catch (error: any) {
    console.error('Admin cancel booking error:', error);
    throw error;
  }
}

/**
 * Approve refund (admin only)
 */
export async function approveRefund(
  billingId: string,
  reason: string,
  token: string
): Promise<any> {
  try {
    const response = await fetch(`/api/billing/billings/${billingId}/refund/approve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ reason }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to approve refund');
    }

    return await response.json();
  } catch (error: any) {
    console.error('Approve refund error:', error);
    throw error;
  }
}

/**
 * Reject refund (admin only)
 */
export async function rejectRefund(
  billingId: string,
  reason: string,
  token: string
): Promise<any> {
  try {
    const response = await fetch(`/api/billing/billings/${billingId}/refund/reject`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ reason }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to reject refund');
    }

    return await response.json();
  } catch (error: any) {
    console.error('Reject refund error:', error);
    throw error;
  }
}

/**
 * Get billing by booking ID
 */
export async function getBillingByBookingId(
  bookingId: string,
  token: string
): Promise<any> {
  try {
    const url = `/api/billing/billings?booking_id=${bookingId}`;
    console.log('Fetching billing from:', url);
    
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    console.log('Billing response status:', response.status);

    if (!response.ok) {
      let errorMessage = 'Failed to get billing';
      try {
        const error = await response.json();
        errorMessage = error.detail || error.message || errorMessage;
      } catch (e) {
        errorMessage = response.statusText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    const data = await response.json();
    console.log('Billing response data:', data);
    
    // Handle both single billing and list response
    if (data.billing) {
      return data.billing;
    }
    if (data.billings && data.billings.length > 0) {
      return data.billings[0];
    }
    
    return null;
  } catch (error: any) {
    console.error('Get billing error:', error);
    
    // Handle network errors
    if (error instanceof TypeError) {
      if (error.message.includes('fetch') || error.message.includes('Failed to fetch')) {
        throw new Error('Network error: Could not connect to billing service. Please check if the service is running.');
      }
      throw new Error(`Network error: ${error.message}`);
    }
    
    throw error;
  }
}

