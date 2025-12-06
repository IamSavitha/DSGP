import React, { useState } from 'react';
import { X, CreditCard, Lock, CheckCircle, Loader2, Receipt } from 'lucide-react';
import { processPayment, PaymentRequest, BillingResponse } from '../api/billing';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

interface PaymentModalProps {
  bookingId: string;
  bookingType: 'flight' | 'hotel' | 'car';
  amount: number;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (billing: BillingResponse) => void;
}

const PaymentModal: React.FC<PaymentModalProps> = ({
  bookingId,
  bookingType,
  amount,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const [paymentMethod, setPaymentMethod] = useState<'credit_card' | 'debit_card' | 'paypal' | 'bank_transfer'>('credit_card');
  const [cardNumber, setCardNumber] = useState('');
  const [cardExpiry, setCardExpiry] = useState('');
  const [cardCvv, setCardCvv] = useState('');
  const [cardholderName, setCardholderName] = useState('');
  const [paypalEmail, setPaypalEmail] = useState('');
  const [billingAddress, setBillingAddress] = useState('');
  const [billingCity, setBillingCity] = useState('');
  const [billingState, setBillingState] = useState('');
  const [billingZip, setBillingZip] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [billing, setBilling] = useState<BillingResponse | null>(null);

  // Calculate tax (8.75%)
  const taxRate = 0.0875;
  const subtotal = amount;
  const taxAmount = subtotal * taxRate;
  const totalAmount = subtotal + taxAmount;

  if (!isOpen) return null;

  const handleCardNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/\s/g, '');
    if (value.length <= 16) {
      // Format with spaces every 4 digits
      value = value.match(/.{1,4}/g)?.join(' ') || value;
      setCardNumber(value);
    }
  };

  const handleExpiryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length <= 4) {
      if (value.length >= 2) {
        value = value.slice(0, 2) + '/' + value.slice(2);
      }
      setCardExpiry(value);
    }
  };

  const handleCvvChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length <= 4) {
      setCardCvv(value);
    }
  };

  const validateForm = (): boolean => {
    if (paymentMethod === 'credit_card' || paymentMethod === 'debit_card') {
      if (!cardNumber || cardNumber.replace(/\s/g, '').length < 13) {
        setError('Please enter a valid card number');
        return false;
      }
      if (!cardExpiry || !/^(0[1-9]|1[0-2])\/([0-9]{2})$/.test(cardExpiry)) {
        setError('Please enter a valid expiry date (MM/YY)');
        return false;
      }
      if (!cardCvv || cardCvv.length < 3) {
        setError('Please enter a valid CVV');
        return false;
      }
      if (!cardholderName) {
        setError('Please enter cardholder name');
        return false;
      }
    } else if (paymentMethod === 'paypal') {
      if (!paypalEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(paypalEmail)) {
        setError('Please enter a valid PayPal email');
        return false;
      }
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!token || !user) {
      setError('Please log in to process payment');
      setTimeout(() => {
        navigate('/login');
      }, 2000);
      return;
    }

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const paymentData: PaymentRequest = {
        booking_id: bookingId,
        payment_method: paymentMethod,
        card_number: paymentMethod === 'credit_card' || paymentMethod === 'debit_card' 
          ? cardNumber.replace(/\s/g, '') 
          : undefined,
        card_expiry: paymentMethod === 'credit_card' || paymentMethod === 'debit_card' 
          ? cardExpiry 
          : undefined,
        card_cvv: paymentMethod === 'credit_card' || paymentMethod === 'debit_card' 
          ? cardCvv 
          : undefined,
        cardholder_name: paymentMethod === 'credit_card' || paymentMethod === 'debit_card' 
          ? cardholderName 
          : undefined,
        paypal_email: paymentMethod === 'paypal' ? paypalEmail : undefined,
        billing_address: billingAddress || undefined,
        billing_city: billingCity || undefined,
        billing_state: billingState || undefined,
        billing_zip: billingZip || undefined,
      };

      const billingResponse = await processPayment(paymentData, token);
      setBilling(billingResponse);
      setSuccess(true);

      if (onSuccess) {
        onSuccess(billingResponse);
      }
    } catch (err: any) {
      console.error('Payment error:', err);
      setError(err.message || 'Payment processing failed. Please try again.');
      setLoading(false);
    }
  };

  if (success && billing) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-4">
        <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 space-y-6">
          <div className="text-center">
            <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Payment Successful!</h2>
            <p className="text-slate-600">Your payment has been processed successfully.</p>
          </div>

          <div className="bg-slate-50 rounded-lg p-4 space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-600">Invoice Number:</span>
              <span className="font-semibold text-slate-900">{billing.invoice_number}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Amount:</span>
              <span className="font-semibold text-slate-900">${totalAmount.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">Payment Method:</span>
              <span className="font-semibold text-slate-900 capitalize">
                {billing.payment_method.replace('_', ' ')}
                {billing.card_last_four && ` •••• ${billing.card_last_four}`}
              </span>
            </div>
          </div>

          <div className="flex space-x-3">
            <button
              onClick={() => {
                onClose();
                navigate('/bookings');
              }}
              className="flex-1 bg-slate-900 text-white py-2.5 px-4 rounded-lg font-medium hover:bg-slate-800 transition-colors"
            >
              View Bookings
            </button>
            <button
              onClick={onClose}
              className="flex-1 bg-slate-100 text-slate-900 py-2.5 px-4 rounded-lg font-medium hover:bg-slate-200 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-6 space-y-6 my-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Complete Payment</h2>
            <p className="text-sm text-slate-600 mt-1">Booking ID: {bookingId}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-slate-600" />
          </button>
        </div>

        {/* Amount Summary */}
        <div className="bg-gradient-to-r from-slate-50 to-slate-100 rounded-lg p-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-slate-600">Subtotal:</span>
            <span className="font-medium text-slate-900">${subtotal.toFixed(2)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-600">Tax (8.75%):</span>
            <span className="font-medium text-slate-900">${taxAmount.toFixed(2)}</span>
          </div>
          <div className="border-t border-slate-200 pt-2 mt-2">
            <div className="flex justify-between">
              <span className="font-semibold text-slate-900">Total:</span>
              <span className="font-bold text-xl text-slate-900">${totalAmount.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Payment Method Selection */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Payment Method
            </label>
            <div className="grid grid-cols-2 gap-3">
              {(['credit_card', 'debit_card', 'paypal', 'bank_transfer'] as const).map((method) => (
                <button
                  key={method}
                  type="button"
                  onClick={() => setPaymentMethod(method)}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    paymentMethod === method
                      ? 'border-slate-900 bg-slate-50'
                      : 'border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <span className="text-sm font-medium capitalize">
                    {method.replace('_', ' ')}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Card Details */}
          {(paymentMethod === 'credit_card' || paymentMethod === 'debit_card') && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">
                  Card Number
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <CreditCard className="h-5 w-5 text-slate-400" />
                  </div>
                  <input
                    type="text"
                    value={cardNumber}
                    onChange={handleCardNumberChange}
                    placeholder="1234 5678 9012 3456"
                    className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
                    maxLength={19}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">
                    Expiry Date
                  </label>
                  <input
                    type="text"
                    value={cardExpiry}
                    onChange={handleExpiryChange}
                    placeholder="MM/YY"
                    className="block w-full py-2.5 px-3 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
                    maxLength={5}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">
                    CVV
                  </label>
                  <input
                    type="text"
                    value={cardCvv}
                    onChange={handleCvvChange}
                    placeholder="123"
                    className="block w-full py-2.5 px-3 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
                    maxLength={4}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">
                  Cardholder Name
                </label>
                <input
                  type="text"
                  value={cardholderName}
                  onChange={(e) => setCardholderName(e.target.value)}
                  placeholder="John Doe"
                  className="block w-full py-2.5 px-3 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
                />
              </div>
            </div>
          )}

          {/* PayPal Email */}
          {paymentMethod === 'paypal' && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                PayPal Email
              </label>
              <input
                type="email"
                value={paypalEmail}
                onChange={(e) => setPaypalEmail(e.target.value)}
                placeholder="your.email@example.com"
                className="block w-full py-2.5 px-3 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
          )}

          {/* Billing Address (Optional) */}
          <div className="space-y-4">
            <h3 className="text-sm font-medium text-slate-700">Billing Address (Optional)</h3>
            <div>
              <input
                type="text"
                value={billingAddress}
                onChange={(e) => setBillingAddress(e.target.value)}
                placeholder="Street Address"
                className="block w-full py-2.5 px-3 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="col-span-2">
                <input
                  type="text"
                  value={billingCity}
                  onChange={(e) => setBillingCity(e.target.value)}
                  placeholder="City"
                  className="block w-full py-2.5 px-3 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
                />
              </div>
              <div>
                <input
                  type="text"
                  value={billingState}
                  onChange={(e) => setBillingState(e.target.value)}
                  placeholder="State"
                  className="block w-full py-2.5 px-3 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
                  maxLength={2}
                />
              </div>
            </div>
            <div>
              <input
                type="text"
                value={billingZip}
                onChange={(e) => setBillingZip(e.target.value)}
                placeholder="ZIP Code"
                className="block w-full py-2.5 px-3 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
          </div>

          {/* Security Notice */}
          <div className="flex items-start space-x-2 bg-slate-50 p-3 rounded-lg">
            <Lock className="w-5 h-5 text-slate-600 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-slate-600">
              Your payment information is secure and encrypted. We only store the last 4 digits of your card for your records.
            </p>
          </div>

          {/* Submit Button */}
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-slate-100 text-slate-900 py-2.5 px-4 rounded-lg font-medium hover:bg-slate-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-slate-900 text-white py-2.5 px-4 rounded-lg font-medium hover:bg-slate-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Lock className="w-4 h-4" />
                  <span>Pay ${totalAmount.toFixed(2)}</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PaymentModal;

