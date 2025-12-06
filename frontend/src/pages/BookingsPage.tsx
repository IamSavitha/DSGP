import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getUserBookings, cancelBooking, BookingResponse } from '../api/bookings';
import { Calendar, Plane, Hotel, Car, X, CheckCircle, Clock, XCircle, AlertCircle } from 'lucide-react';

const BookingsPage: React.FC = () => {
  const { user, token, isAuthenticated } = useAuth();
  const [bookings, setBookings] = useState<BookingResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'flight' | 'hotel' | 'car'>('all');
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'confirmed' | 'cancelled' | 'completed'>('all');

  useEffect(() => {
    if (isAuthenticated && user && token) {
      loadBookings();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated, user, token, filter, statusFilter]);

  const loadBookings = async () => {
    if (!user || !token) return;
    
    setLoading(true);
    setError(null);
    try {
      const bookingType = filter !== 'all' ? filter : undefined;
      const status = statusFilter !== 'all' ? statusFilter : undefined;
      const data = await getUserBookings(user.user_id, token, bookingType, status);
      setBookings(data);
    } catch (err: any) {
      console.error('Error loading bookings:', err);
      setError(err.message || 'Failed to load bookings');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (bookingId: string, status: string) => {
    if (!token) return;
    
    // Check if booking is confirmed (paid) - need to process refund
    const isConfirmed = status.toLowerCase() === 'confirmed';
    const refundMessage = isConfirmed 
      ? 'This booking is confirmed and paid. A refund will be processed. Are you sure you want to cancel?'
      : 'Are you sure you want to cancel this booking?';
    
    if (!window.confirm(refundMessage)) {
      return;
    }

    try {
      // For confirmed bookings, request refund
      await cancelBooking(bookingId, token, 'Cancelled by user', isConfirmed);
      
      if (isConfirmed) {
        alert('Booking cancelled successfully. Refund will be processed.');
      } else {
        alert('Booking cancelled successfully.');
      }
      
      // Reload bookings after cancellation
      loadBookings();
    } catch (err: any) {
      console.error('Error cancelling booking:', err);
      alert(err.message || 'Failed to cancel booking');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'confirmed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'refund_pending':
        return <Clock className="w-5 h-5 text-orange-500" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-blue-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'confirmed':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'cancelled':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'refund_pending':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'completed':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getBookingIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'flight':
        return <Plane className="w-6 h-6" />;
      case 'hotel':
        return <Hotel className="w-6 h-6" />;
      case 'car':
        return <Car className="w-6 h-6" />;
      default:
        return <Calendar className="w-6 h-6" />;
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-slate-900 mb-4">Please Sign In</h1>
          <p className="text-slate-600 mb-6">You need to be signed in to view your bookings.</p>
          <a href="/login" className="btn-primary inline-block">Sign In</a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-extrabold text-slate-900 mb-8 text-center">My Bookings</h1>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Booking Type</label>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value as any)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Types</option>
                <option value="flight">Flights</option>
                <option value="hotel">Hotels</option>
                <option value="car">Cars</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Status</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as any)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="confirmed">Confirmed</option>
                <option value="refund_pending">Refund Pending</option>
                <option value="cancelled">Cancelled</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <p className="mt-4 text-slate-600">Loading your bookings...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-xl mb-8">
            <p className="font-bold">Error:</p>
            <p>{error}</p>
            <button
              onClick={loadBookings}
              className="mt-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Bookings List */}
        {!loading && !error && (
          <>
            {bookings.length === 0 ? (
              <div className="bg-white rounded-xl shadow-lg p-12 text-center">
                <Calendar className="w-16 h-16 text-slate-400 mx-auto mb-4" />
                <h2 className="text-2xl font-semibold text-slate-900 mb-2">No Bookings Found</h2>
                <p className="text-slate-600 mb-6">
                  {filter !== 'all' || statusFilter !== 'all'
                    ? 'No bookings match your current filters.'
                    : "You haven't made any bookings yet."}
                </p>
                {(filter !== 'all' || statusFilter !== 'all') && (
                  <button
                    onClick={() => {
                      setFilter('all');
                      setStatusFilter('all');
                    }}
                    className="btn-primary"
                  >
                    Clear Filters
                  </button>
                )}
              </div>
            ) : (
              <div className="space-y-6">
                {bookings.map((booking) => (
                  <div
                    key={booking.booking_id}
                    className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-4">
                        <div className="bg-blue-100 p-3 rounded-lg">
                          {getBookingIcon(booking.booking_type)}
                        </div>
                        <div>
                          <h3 className="text-xl font-semibold text-slate-900 capitalize">
                            {booking.booking_type} Booking
                          </h3>
                          <p className="text-sm text-slate-500">Booking ID: {booking.booking_id}</p>
                        </div>
                      </div>
                      <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg border ${getStatusColor(booking.status)}`}>
                        {getStatusIcon(booking.status)}
                        <span className="font-medium capitalize">{booking.status}</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-slate-500 mb-1">Check-in Date</p>
                        <p className="font-medium text-slate-900">{formatDate(booking.check_in_date)}</p>
                      </div>
                      {booking.check_out_date && (
                        <div>
                          <p className="text-sm text-slate-500 mb-1">Check-out Date</p>
                          <p className="font-medium text-slate-900">{formatDate(booking.check_out_date)}</p>
                        </div>
                      )}
                      {booking.num_passengers && booking.num_passengers > 0 && (
                        <div>
                          <p className="text-sm text-slate-500 mb-1">Passengers</p>
                          <p className="font-medium text-slate-900">{booking.num_passengers}</p>
                        </div>
                      )}
                      {booking.num_nights && booking.num_nights > 0 && (
                        <div>
                          <p className="text-sm text-slate-500 mb-1">Nights</p>
                          <p className="font-medium text-slate-900">{booking.num_nights}</p>
                        </div>
                      )}
                      <div>
                        <p className="text-sm text-slate-500 mb-1">Listing ID</p>
                        <p className="font-medium text-slate-900">{booking.listing_id}</p>
                      </div>
                      <div>
                        <p className="text-sm text-slate-500 mb-1">Booking Date</p>
                        <p className="font-medium text-slate-900">{formatDate(booking.booking_date || booking.created_at)}</p>
                      </div>
                    </div>

                    <div className="pt-4 border-t border-slate-200">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          {booking.total_amount ? (
                            // Show breakdown if payment was completed (billing info available)
                            <div>
                              <div className="flex items-baseline justify-between mb-1">
                                <p className="text-sm text-slate-500">Subtotal</p>
                                <p className="text-sm font-medium text-slate-700">
                                  ${booking.subtotal ? parseFloat(booking.subtotal.toString()).toFixed(2) : parseFloat(booking.total_price.toString()).toFixed(2)}
                                </p>
                              </div>
                              <div className="flex items-baseline justify-between mb-1">
                                <p className="text-sm text-slate-500">Tax (8.75%)</p>
                                <p className="text-sm font-medium text-slate-700">
                                  ${booking.tax_amount ? parseFloat(booking.tax_amount.toString()).toFixed(2) : '0.00'}
                                </p>
                              </div>
                              <div className="flex items-baseline justify-between pt-2 border-t border-slate-200">
                                <p className="text-sm font-semibold text-slate-700">Total</p>
                                <p className="text-2xl font-bold text-blue-600">
                                  ${parseFloat(booking.total_amount.toString()).toFixed(2)}
                                </p>
                              </div>
                              {booking.invoice_number && (
                                <a
                                  href={`/billing?booking_id=${booking.booking_id}`}
                                  onClick={(e) => {
                                    e.preventDefault();
                                    window.location.href = `/billing?booking_id=${booking.booking_id}`;
                                  }}
                                  className="text-xs text-blue-600 hover:text-blue-800 hover:underline mt-2 inline-block"
                                >
                                  Invoice: {booking.invoice_number} (View Details)
                                </a>
                              )}
                            </div>
                          ) : (
                            // Show booking price only if payment not completed
                            <div>
                              <p className="text-sm text-slate-500 mb-1">Total Price</p>
                              <p className="text-2xl font-bold text-blue-600">
                                ${parseFloat(booking.total_price.toString()).toFixed(2)}
                              </p>
                              <p className="text-xs text-slate-500 mt-1">Payment pending</p>
                            </div>
                          )}
                        </div>
                        <div className="ml-4">
                          {(booking.status.toLowerCase() === 'pending' || booking.status.toLowerCase() === 'confirmed') && (
                            <button
                              onClick={() => handleCancel(booking.booking_id, booking.status)}
                              className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors flex items-center space-x-2"
                            >
                              <X className="w-4 h-4" />
                              <span>
                                {booking.status.toLowerCase() === 'confirmed' ? 'Cancel & Request Refund' : 'Cancel Booking'}
                              </span>
                            </button>
                          )}
                          {booking.status.toLowerCase() === 'refund_pending' && (
                            <div className="px-6 py-2 bg-orange-100 text-orange-800 rounded-lg border border-orange-300">
                              <p className="text-sm font-medium">Refund Pending Admin Approval</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default BookingsPage;
