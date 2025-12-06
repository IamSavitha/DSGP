import React, { useState } from 'react';
import { Plane, Hotel, Car, Search, Calendar, Users, DollarSign, Loader2, AlertCircle, Sparkles, Star, MapPin, ArrowRight } from 'lucide-react';
import { findBundles, Bundle, BundleRequest } from '../api/bundles';
import { useNavigate } from 'react-router-dom';

const BundlesPage: React.FC = () => {
  const [bundles, setBundles] = useState<Bundle[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Search form state
  const [searchParams, setSearchParams] = useState<BundleRequest>({
    origin: '',
    destination: '',
    departure_date: '',
    return_date: '',
    budget: undefined,
    num_travelers: 2,
    preferences: {}
  });

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!searchParams.destination || !searchParams.departure_date) {
      setError('Please provide destination and departure date');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await findBundles(searchParams);
      setBundles(response.bundles || []);
      
      if (response.bundles.length === 0) {
        setError('No bundles found matching your criteria. Try adjusting your search parameters.');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to find bundles. Please try again.');
      console.error('Error finding bundles:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toISOString().split('T')[0];
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  const getFitScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-blue-600 bg-blue-100';
    if (score >= 40) return 'text-orange-600 bg-orange-100';
    return 'text-slate-600 bg-slate-100';
  };

  const handleBundleClick = (bundle: Bundle) => {
    // Navigate to a booking flow or show details
    // For now, we can navigate to the search page with bundle details
    navigate(`/search?bundle_id=${bundle.bundle_id}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-3 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl shadow-lg">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-slate-900">Trip Bundles</h1>
              <p className="text-slate-600 mt-1">Complete packages: Flight + Hotel + Car</p>
            </div>
          </div>
        </div>

        {/* Search Form */}
        <div className="bg-white border-2 border-slate-300 rounded-xl p-6 mb-8 shadow-lg">
          <form onSubmit={handleSearch} className="space-y-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Origin */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  <MapPin className="w-4 h-4 inline mr-1" />
                  From (Optional)
                </label>
                <input
                  type="text"
                  placeholder="City or airport code"
                  value={searchParams.origin || ''}
                  onChange={(e) => setSearchParams({ ...searchParams, origin: e.target.value })}
                  className="w-full px-4 py-2 border-2 border-slate-300 rounded-lg text-slate-700 focus:border-slate-700 focus:outline-none"
                />
              </div>

              {/* Destination */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  <MapPin className="w-4 h-4 inline mr-1" />
                  Destination *
                </label>
                <input
                  type="text"
                  placeholder="City or airport code"
                  required
                  value={searchParams.destination}
                  onChange={(e) => setSearchParams({ ...searchParams, destination: e.target.value })}
                  className="w-full px-4 py-2 border-2 border-slate-300 rounded-lg text-slate-700 focus:border-slate-700 focus:outline-none"
                />
              </div>

              {/* Departure Date */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  <Calendar className="w-4 h-4 inline mr-1" />
                  Departure Date *
                </label>
                <input
                  type="date"
                  required
                  value={searchParams.departure_date}
                  onChange={(e) => setSearchParams({ ...searchParams, departure_date: e.target.value })}
                  min={formatDate(new Date().toISOString())}
                  className="w-full px-4 py-2 border-2 border-slate-300 rounded-lg text-slate-700 focus:border-slate-700 focus:outline-none"
                />
              </div>

              {/* Return Date */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  <Calendar className="w-4 h-4 inline mr-1" />
                  Return Date (Optional)
                </label>
                <input
                  type="date"
                  value={searchParams.return_date || ''}
                  onChange={(e) => setSearchParams({ ...searchParams, return_date: e.target.value })}
                  min={searchParams.departure_date || formatDate(new Date().toISOString())}
                  className="w-full px-4 py-2 border-2 border-slate-300 rounded-lg text-slate-700 focus:border-slate-700 focus:outline-none"
                />
              </div>

              {/* Number of Travelers */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  <Users className="w-4 h-4 inline mr-1" />
                  Travelers
                </label>
                <input
                  type="number"
                  min="1"
                  max="9"
                  value={searchParams.num_travelers}
                  onChange={(e) => setSearchParams({ ...searchParams, num_travelers: parseInt(e.target.value) || 1 })}
                  className="w-full px-4 py-2 border-2 border-slate-300 rounded-lg text-slate-700 focus:border-slate-700 focus:outline-none"
                />
              </div>

              {/* Budget */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  <DollarSign className="w-4 h-4 inline mr-1" />
                  Budget (Optional)
                </label>
                <input
                  type="number"
                  min="0"
                  placeholder="Max budget"
                  value={searchParams.budget || ''}
                  onChange={(e) => setSearchParams({ ...searchParams, budget: e.target.value ? parseFloat(e.target.value) : undefined })}
                  className="w-full px-4 py-2 border-2 border-slate-300 rounded-lg text-slate-700 focus:border-slate-700 focus:outline-none"
                />
              </div>
            </div>

            {/* Search Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 px-6 rounded-lg font-semibold hover:from-blue-700 hover:to-blue-800 transition-all flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Finding bundles...</span>
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  <span>Find Bundles</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border-2 border-red-200 rounded-xl flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
            <span className="ml-3 text-slate-700 font-semibold">Finding the best bundles for you...</span>
          </div>
        )}

        {/* Bundles Grid */}
        {!loading && !error && bundles.length > 0 && (
          <>
            <div className="mb-6 flex items-center justify-between">
              <p className="text-slate-600">
                Found <span className="font-bold text-slate-900">{bundles.length}</span> bundle{bundles.length !== 1 ? 's' : ''}
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {bundles.map((bundle) => (
                <div
                  key={bundle.bundle_id}
                  onClick={() => handleBundleClick(bundle)}
                  className="bg-white border-2 border-slate-300 rounded-xl p-6 cursor-pointer hover:shadow-xl hover:border-slate-400 transition-all duration-300 group"
                >
                  {/* Bundle Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-2">
                      <div className="p-2 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg text-white">
                        <Sparkles className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-slate-900">Bundle Package</h3>
                        <p className="text-xs text-slate-500">{bundle.bundle_id}</p>
                      </div>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-xs font-bold ${getFitScoreColor(bundle.fit_score)}`}>
                      Score: {bundle.fit_score.toFixed(1)}
                    </div>
                  </div>

                  {/* Price */}
                  <div className="mb-4 p-4 bg-slate-50 rounded-lg">
                    <div className="flex items-baseline justify-between">
                      <span className="text-sm text-slate-600">Total Package Price</span>
                      <span className="text-3xl font-bold text-blue-600">
                        ${bundle.total_price.toFixed(2)}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">
                      {bundle.num_nights} night{bundle.num_nights !== 1 ? 's' : ''} • {bundle.num_travelers} traveler{bundle.num_travelers !== 1 ? 's' : ''}
                    </p>
                  </div>

                  {/* Flight Info */}
                  <div className="mb-3 p-3 bg-blue-50 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Plane className="w-4 h-4 text-blue-600" />
                      <span className="text-sm font-semibold text-slate-700">Flight</span>
                    </div>
                    <p className="text-sm text-slate-900 font-medium">{bundle.flight.airline}</p>
                    <p className="text-xs text-slate-600">
                      {bundle.flight.route} • ${bundle.flight.price.toFixed(2)}
                      {bundle.flight.duration_minutes > 0 && ` • ${formatDuration(bundle.flight.duration_minutes)}`}
                    </p>
                  </div>

                  {/* Hotel Info */}
                  <div className="mb-3 p-3 bg-purple-50 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Hotel className="w-4 h-4 text-purple-600" />
                      <span className="text-sm font-semibold text-slate-700">Hotel</span>
                    </div>
                    <p className="text-sm text-slate-900 font-medium">{bundle.hotel.name}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      {bundle.hotel.stars > 0 && (
                        <div className="flex items-center space-x-1">
                          {Array.from({ length: bundle.hotel.stars }).map((_, i) => (
                            <Star key={i} className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                          ))}
                        </div>
                      )}
                      <p className="text-xs text-slate-600">
                        {bundle.hotel.city} • ${bundle.hotel.total_price.toFixed(2)} total
                      </p>
                    </div>
                  </div>

                  {/* Car Info */}
                  <div className="mb-4 p-3 bg-green-50 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Car className="w-4 h-4 text-green-600" />
                      <span className="text-sm font-semibold text-slate-700">Car Rental</span>
                    </div>
                    <p className="text-sm text-slate-900 font-medium">
                      {bundle.car.make} {bundle.car.model}
                    </p>
                    <p className="text-xs text-slate-600">
                      {bundle.car.car_type} • {bundle.car.provider} • ${bundle.car.total_price.toFixed(2)} total
                    </p>
                  </div>

                  {/* Explanation */}
                  {bundle.explanation && (
                    <div className="mb-4 p-3 bg-slate-50 rounded-lg">
                      <p className="text-sm text-slate-700 italic">{bundle.explanation}</p>
                    </div>
                  )}

                  {/* View Bundle Button */}
                  <button className="w-full mt-4 px-4 py-2 bg-gradient-to-r from-slate-700 to-slate-800 text-white rounded-lg font-semibold hover:from-slate-800 hover:to-slate-900 transition-all flex items-center justify-center space-x-2 group-hover:shadow-lg">
                    <span>View Bundle Details</span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>
              ))}
            </div>
          </>
        )}

        {/* Empty State */}
        {!loading && !error && bundles.length === 0 && (
          <div className="text-center py-20">
            <Sparkles className="w-16 h-16 text-slate-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-700 mb-2">No bundles found</h3>
            <p className="text-slate-600">Enter your travel details above to find bundle packages</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BundlesPage;

