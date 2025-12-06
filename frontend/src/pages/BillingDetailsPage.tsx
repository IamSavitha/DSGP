import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { getBilling, getInvoice, BillingResponse } from '../api/billing';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Receipt, Search, Loader2, ArrowLeft, Download, CheckCircle, Clock, XCircle, AlertCircle } from 'lucide-react';

const BillingDetailsPage: React.FC = () => {
  const { token, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const billingIdFromUrl = searchParams.get('id');
  const bookingIdFromUrl = searchParams.get('booking_id');

  const [billingId, setBillingId] = useState(billingIdFromUrl || '');
  const [billing, setBilling] = useState<BillingResponse | null>(null);
  const [invoice, setInvoice] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showInvoice, setShowInvoice] = useState(false);

  // If billing ID or booking ID is in URL, load it automatically
  React.useEffect(() => {
    if (billingIdFromUrl && isAuthenticated && token) {
      handleSearch(billingIdFromUrl);
    } else if (bookingIdFromUrl && isAuthenticated && token) {
      // Fetch billing by booking ID
      handleSearchByBookingId(bookingIdFromUrl);
    }
  }, [billingIdFromUrl, bookingIdFromUrl, isAuthenticated, token]);

  const handleSearchByBookingId = async (bookingId: string) => {
    if (!token) {
      setError('Please log in to view billing details');
      navigate('/login');
      return;
    }

    setLoading(true);
    setError(null);
    setBilling(null);
    setInvoice(null);

    try {
      // Search for billing by booking_id
      const response = await fetch(`/api/billing/billings?booking_id=${bookingId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to retrieve billing record');
      }

      const data = await response.json();
      if (data.billings && data.billings.length > 0) {
        setBilling(data.billings[0]);
        setBillingId(data.billings[0].billing_id);
      } else {
        setError('No billing record found for this booking');
      }
    } catch (err: any) {
      console.error('Error fetching billing:', err);
      setError(err.message || 'Failed to retrieve billing record');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (id?: string) => {
    const searchId = id || billingId.trim();
    if (!searchId) {
      setError('Please enter a billing ID');
      return;
    }

    if (!token) {
      setError('Please log in to view billing details');
      navigate('/login');
      return;
    }

    setLoading(true);
    setError(null);
    setBilling(null);
    setInvoice(null);

    try {
      const billingData = await getBilling(searchId, token);
      setBilling(billingData);
      setBillingId(searchId);
    } catch (err: any) {
      console.error('Error fetching billing:', err);
      setError(err.message || 'Failed to retrieve billing record');
    } finally {
      setLoading(false);
    }
  };

  const handleGetInvoice = async () => {
    if (!billing || !token) return;

    setLoading(true);
    setError(null);

    try {
      const invoiceData = await getInvoice(billing.billing_id, token);
      setInvoice(invoiceData);
      setShowInvoice(true);
    } catch (err: any) {
      console.error('Error fetching invoice:', err);
      setError(err.message || 'Failed to retrieve invoice');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-600" />;
      case 'refund_pending':
        return <Clock className="w-5 h-5 text-orange-600" />;
      case 'refunded':
        return <CheckCircle className="w-5 h-5 text-blue-600" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'refund_pending':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'refunded':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <AlertCircle className="w-16 h-16 text-slate-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-slate-900 mb-2">Authentication Required</h2>
          <p className="text-slate-600 mb-6">Please log in to view billing details</p>
          <button
            onClick={() => navigate('/login')}
            className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold py-3 px-6 rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/bookings')}
            className="flex items-center text-slate-600 hover:text-slate-900 mb-4 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            <span>Back to Bookings</span>
          </button>
          <h1 className="text-3xl font-bold text-slate-900 flex items-center">
            <Receipt className="w-8 h-8 mr-3 text-blue-600" />
            Billing Details
          </h1>
          <p className="text-slate-600 mt-2">Retrieve and view billing records by ID</p>
        </div>

        {/* Search Form */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6 border-2 border-slate-200">
          <div className="flex gap-4">
            <div className="flex-1">
              <label className="block text-sm font-semibold text-slate-700 mb-2">
                Billing ID
              </label>
              <input
                type="text"
                value={billingId}
                onChange={(e) => setBillingId(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Enter billing ID (e.g., BILL-12345678)"
                className="w-full px-4 py-3 border-2 border-slate-300 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all bg-white text-slate-900"
              />
            </div>
            <div className="flex items-end">
              <button
                onClick={() => handleSearch()}
                disabled={loading || !billingId.trim()}
                className="bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold py-3 px-8 rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-5 h-5" />
                    <span>Search</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-2 border-red-200 rounded-xl p-4 mb-6">
            <div className="flex items-center">
              <XCircle className="w-5 h-5 text-red-600 mr-2" />
              <p className="text-red-800 font-medium">{error}</p>
            </div>
          </div>
        )}

        {/* Billing Details */}
        {billing && (
          <div className="bg-white rounded-2xl shadow-lg p-6 border-2 border-slate-200">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-slate-900">Billing Information</h2>
              <div className={`px-4 py-2 rounded-lg border-2 flex items-center space-x-2 ${getStatusColor(billing.payment_status)}`}>
                {getStatusIcon(billing.payment_status)}
                <span className="font-semibold capitalize">{billing.payment_status.replace('_', ' ')}</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Left Column */}
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-slate-500 mb-1">Billing ID</p>
                  <p className="font-mono text-lg font-semibold text-slate-900">{billing.billing_id}</p>
                </div>

                {billing.invoice_number && (
                  <div>
                    <p className="text-sm text-slate-500 mb-1">Invoice Number</p>
                    <p className="font-mono text-lg font-semibold text-blue-600">{billing.invoice_number}</p>
                  </div>
                )}

                <div>
                  <p className="text-sm text-slate-500 mb-1">User ID</p>
                  <p className="font-medium text-slate-900">{billing.user_id}</p>
                </div>

                <div>
                  <p className="text-sm text-slate-500 mb-1">Booking ID</p>
                  <p className="font-mono text-slate-900">{billing.booking_id}</p>
                </div>

                <div>
                  <p className="text-sm text-slate-500 mb-1">Booking Type</p>
                  <p className="font-medium text-slate-900 capitalize">{billing.booking_type}</p>
                </div>

                <div>
                  <p className="text-sm text-slate-500 mb-1">Payment Method</p>
                  <p className="font-medium text-slate-900 capitalize">{billing.payment_method.replace('_', ' ')}</p>
                </div>
              </div>

              {/* Right Column */}
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-slate-500 mb-1">Transaction Date</p>
                  <p className="font-medium text-slate-900">{formatDate(billing.transaction_date)}</p>
                </div>

                {billing.card_last_four && (
                  <div>
                    <p className="text-sm text-slate-500 mb-1">Card Last 4 Digits</p>
                    <p className="font-mono text-lg font-semibold text-slate-900">**** {billing.card_last_four}</p>
                  </div>
                )}

                <div>
                  <p className="text-sm text-slate-500 mb-1">Subtotal</p>
                  <p className="text-xl font-bold text-slate-900">
                    ${typeof billing.subtotal === 'number' ? billing.subtotal.toFixed(2) : parseFloat(billing.subtotal.toString()).toFixed(2)}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-slate-500 mb-1">Tax Amount (8.75%)</p>
                  <p className="text-xl font-bold text-slate-900">
                    ${typeof billing.tax_amount === 'number' ? billing.tax_amount.toFixed(2) : parseFloat(billing.tax_amount.toString()).toFixed(2)}
                  </p>
                </div>

                <div className="pt-4 border-t-2 border-slate-200">
                  <p className="text-sm text-slate-500 mb-1">Total Amount</p>
                  <p className="text-3xl font-bold text-blue-600">
                    ${typeof billing.total_amount === 'number' ? billing.total_amount.toFixed(2) : parseFloat(billing.total_amount.toString()).toFixed(2)}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-slate-500 mb-1">Created At</p>
                  <p className="font-medium text-slate-900">{formatDate(billing.created_at)}</p>
                </div>

                <div>
                  <p className="text-sm text-slate-500 mb-1">Updated At</p>
                  <p className="font-medium text-slate-900">{formatDate(billing.updated_at)}</p>
                </div>
              </div>
            </div>

            {/* Invoice Button */}
            {billing.invoice_number && (
              <div className="mt-6 pt-6 border-t border-slate-200">
                <button
                  onClick={handleGetInvoice}
                  disabled={loading}
                  className="bg-gradient-to-r from-green-600 to-green-700 text-white font-bold py-3 px-6 rounded-xl hover:from-green-700 hover:to-green-800 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  <Download className="w-5 h-5" />
                  <span>{showInvoice ? 'Refresh Invoice' : 'View Full Invoice'}</span>
                </button>
              </div>
            )}

            {/* Invoice Details */}
            {showInvoice && invoice && (
              <div className="mt-6 pt-6 border-t-2 border-slate-200">
                <h3 className="text-xl font-bold text-slate-900 mb-4">Invoice Details</h3>
                <div className="bg-slate-50 rounded-xl p-6 space-y-3">
                  <div className="flex justify-between">
                    <span className="text-slate-600">Invoice Number:</span>
                    <span className="font-mono font-semibold text-slate-900">{invoice.invoice_number}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">User Name:</span>
                    <span className="font-medium text-slate-900">{invoice.user_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">User Email:</span>
                    <span className="font-medium text-slate-900">{invoice.user_email}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Booking Type:</span>
                    <span className="font-medium text-slate-900 capitalize">{invoice.booking_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Subtotal:</span>
                    <span className="font-medium text-slate-900">${parseFloat(invoice.subtotal).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Tax Amount:</span>
                    <span className="font-medium text-slate-900">${parseFloat(invoice.tax_amount).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between pt-3 border-t border-slate-300">
                    <span className="text-lg font-semibold text-slate-900">Total Amount:</span>
                    <span className="text-lg font-bold text-blue-600">${parseFloat(invoice.total_amount).toFixed(2)}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default BillingDetailsPage;

