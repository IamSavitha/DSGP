/**
 * Billing and Payment API functions
 */

// Always use proxy URLs - Vite dev server will route them correctly
const BILLING_API_BASE_URL = '/api/billing';

export interface PaymentRequest {
  booking_id: string;
  payment_method: 'credit_card' | 'debit_card' | 'paypal' | 'bank_transfer';
  card_number?: string;
  card_expiry?: string; // MM/YY format
  card_cvv?: string;
  cardholder_name?: string;
  paypal_email?: string;
  billing_address?: string;
  billing_city?: string;
  billing_state?: string;
  billing_zip?: string;
}

export interface BillingResponse {
  billing_id: string;
  user_id: string;
  booking_id: string;
  booking_type: string;
  transaction_date: string;
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  payment_method: string;
  payment_status: string;
  card_last_four?: string;
  invoice_number?: string;
  created_at: string;
  updated_at: string;
}

export interface InvoiceResponse {
  invoice_number: string;
  billing_id: string;
  user_id: string;
  booking_id: string;
  user_name: string;
  user_email: string;
  booking_type: string;
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  payment_method: string;
  payment_status: string;
  transaction_date: string;
}

/**
 * Process a payment for a booking
 */
export async function processPayment(
  payment: PaymentRequest,
  token: string
): Promise<BillingResponse> {
  try {
    const response = await fetch(`${BILLING_API_BASE_URL}/payments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(payment),
    });

    if (!response.ok) {
      const error = await response.json();
      const errorMessage = error.detail || error.message || 'Payment processing failed';
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error: any) {
    console.error('Payment error:', error);
    if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
      throw new Error('Unable to connect to billing service. Please check if the service is running.');
    }
    throw error;
  }
}

/**
 * Get billing record by ID
 */
export async function getBilling(
  billingId: string,
  token: string
): Promise<BillingResponse> {
  try {
    const response = await fetch(`${BILLING_API_BASE_URL}/billings/${billingId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      const errorMessage = error.detail || error.message || 'Failed to get billing record';
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error: any) {
    console.error('Get billing error:', error);
    throw error;
  }
}

/**
 * Get invoice details
 */
export async function getInvoice(
  billingId: string,
  token: string
): Promise<InvoiceResponse> {
  try {
    const response = await fetch(`${BILLING_API_BASE_URL}/billings/${billingId}/invoice`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      const errorMessage = error.detail || error.message || 'Failed to get invoice';
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error: any) {
    console.error('Get invoice error:', error);
    throw error;
  }
}

/**
 * Search billing records
 */
export interface BillingSearchParams {
  user_id?: string;
  booking_type?: string;
  payment_status?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
}

export interface BillingListResponse {
  billings: BillingResponse[];
  total_count: number;
  total_amount: number;
  page: number;
  page_size: number;
}

export async function searchBillings(
  params: BillingSearchParams,
  token: string
): Promise<BillingListResponse> {
  try {
    const queryParams = new URLSearchParams();
    if (params.user_id) queryParams.append('user_id', params.user_id);
    if (params.booking_type) queryParams.append('booking_type', params.booking_type);
    if (params.payment_status) queryParams.append('payment_status', params.payment_status);
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.page_size) queryParams.append('page_size', params.page_size.toString());

    const response = await fetch(`${BILLING_API_BASE_URL}/billings?${queryParams.toString()}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      const errorMessage = error.detail || error.message || 'Failed to search billings';
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error: any) {
    console.error('Search billings error:', error);
    throw error;
  }
}

