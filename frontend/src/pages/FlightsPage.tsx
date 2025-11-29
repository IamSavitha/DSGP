import React, { useState } from 'react';
import { Plane, Calendar, MapPin, Users, Search, Filter, ArrowRight, Clock, DollarSign, Star } from 'lucide-react';

interface Flight {
  id: string;
  airline: string;
  from: string;
  to: string;
  departure: string;
  arrival: string;
  duration: string;
  price: number;
  class: string;
  stops: number;
  rating: number;
}

const FlightsPage: React.FC = () => {
  const [showFilters, setShowFilters] = useState(false);

  // Mock flight data
  const flights: Flight[] = [
    {
      id: '1',
      airline: 'United Airlines',
      from: 'JFK',
      to: 'LAX',
      departure: '08:00 AM',
      arrival: '11:30 AM',
      duration: '5h 30m',
      price: 299,
      class: 'Economy',
      stops: 0,
      rating: 4.5
    },
    {
      id: '2',
      airline: 'Delta',
      from: 'JFK',
      to: 'LAX',
      departure: '10:30 AM',
      arrival: '02:15 PM',
      duration: '5h 45m',
      price: 349,
      class: 'Economy',
      stops: 0,
      rating: 4.7
    },
    {
      id: '3',
      airline: 'American Airlines',
      from: 'JFK',
      to: 'LAX',
      departure: '02:00 PM',
      arrival: '05:45 PM',
      duration: '5h 45m',
      price: 279,
      class: 'Economy',
      stops: 1,
      rating: 4.3
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30">
      {/* Search Header */}
      <div className="bg-gradient-to-r from-slate-700 to-slate-800 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-8 animate-slide-down">Search Flights</h1>

          {/* Search Form */}
          <div className="glass rounded-2xl p-6 border-2 border-white/20 shadow-2xl animate-scale-in">
            <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider">From</label>
                <div className="flex items-center border-2 border-white/30 rounded-xl px-4 py-3 bg-white/10 focus-within:border-white focus-within:bg-white/20 transition-all">
                  <MapPin className="text-white mr-3 flex-shrink-0" size={18} />
                  <input
                    type="text"
                    placeholder="JFK"
                    className="w-full outline-none text-sm font-semibold text-white placeholder:text-white/60 bg-transparent"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider">To</label>
                <div className="flex items-center border-2 border-white/30 rounded-xl px-4 py-3 bg-white/10 focus-within:border-white focus-within:bg-white/20 transition-all">
                  <MapPin className="text-white mr-3 flex-shrink-0" size={18} />
                  <input
                    type="text"
                    placeholder="LAX"
                    className="w-full outline-none text-sm font-semibold text-white placeholder:text-white/60 bg-transparent"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider">Departure</label>
                <div className="flex items-center border-2 border-white/30 rounded-xl px-4 py-3 bg-white/10 focus-within:border-white focus-within:bg-white/20 transition-all">
                  <Calendar className="text-white mr-3 flex-shrink-0" size={18} />
                  <input
                    type="date"
                    className="w-full outline-none text-sm font-semibold text-white placeholder:text-white/60 bg-transparent"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider">Return</label>
                <div className="flex items-center border-2 border-white/30 rounded-xl px-4 py-3 bg-white/10 focus-within:border-white focus-within:bg-white/20 transition-all">
                  <Calendar className="text-white mr-3 flex-shrink-0" size={18} />
                  <input
                    type="date"
                    className="w-full outline-none text-sm font-semibold text-white placeholder:text-white/60 bg-transparent"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider">Travelers</label>
                <div className="flex items-center border-2 border-white/30 rounded-xl px-4 py-3 bg-white/10 focus-within:border-white focus-within:bg-white/20 transition-all">
                  <Users className="text-white mr-3 flex-shrink-0" size={18} />
                  <input
                    type="number"
                    placeholder="1"
                    min="1"
                    className="w-full outline-none text-sm font-semibold text-white placeholder:text-white/60 bg-transparent"
                  />
                </div>
              </div>
            </div>

            <button className="w-full mt-6 bg-white text-slate-800 hover:bg-slate-50 font-bold py-4 px-6 rounded-xl flex items-center justify-center space-x-3 transition-all duration-200 shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] group">
              <Search size={20} className="group-hover:rotate-90 transition-transform duration-300" />
              <span className="text-base">Search Flights</span>
              <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform duration-300" />
            </button>
          </div>
        </div>
      </div>

      {/* Results Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold text-slate-900">Available Flights</h2>
            <p className="text-slate-600 mt-1">{flights.length} flights found</p>
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn-secondary flex items-center space-x-2 py-2.5 px-5"
          >
            <Filter size={18} />
            <span>Filters</span>
          </button>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Filters Sidebar */}
          {showFilters && (
            <div className="lg:col-span-1 animate-slide-up">
              <div className="card p-6 sticky top-24">
                <h3 className="text-lg font-bold text-slate-900 mb-6">Filter Results</h3>

                {/* Stops Filter */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Stops</h4>
                  <div className="space-y-2">
                    {['Non-stop', '1 stop', '2+ stops'].map((option) => (
                      <label key={option} className="flex items-center space-x-2 cursor-pointer group">
                        <input type="checkbox" className="rounded text-slate-600 focus:ring-slate-500" />
                        <span className="text-sm text-slate-600 group-hover:text-slate-900">{option}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Price Range */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Price Range</h4>
                  <input type="range" min="0" max="1000" className="w-full" />
                  <div className="flex justify-between text-xs text-slate-600 mt-2">
                    <span>$0</span>
                    <span>$1000+</span>
                  </div>
                </div>

                {/* Airlines */}
                <div>
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Airlines</h4>
                  <div className="space-y-2">
                    {['United Airlines', 'Delta', 'American Airlines'].map((airline) => (
                      <label key={airline} className="flex items-center space-x-2 cursor-pointer group">
                        <input type="checkbox" className="rounded text-slate-600 focus:ring-slate-500" />
                        <span className="text-sm text-slate-600 group-hover:text-slate-900">{airline}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Flight Results */}
          <div className={showFilters ? 'lg:col-span-2' : 'lg:col-span-3'}>
            <div className="space-y-4">
              {flights.map((flight, index) => (
                <FlightCard key={flight.id} flight={flight} delay={index * 100} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

interface FlightCardProps {
  flight: Flight;
  delay: number;
}

const FlightCard: React.FC<FlightCardProps> = ({ flight, delay }) => (
  <div
    className="card-interactive p-6 animate-slide-up"
    style={{ animationDelay: `${delay}ms` }}
  >
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
      {/* Flight Info */}
      <div className="flex-1">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-slate-100 rounded-lg">
            <Plane className="text-slate-700" size={24} />
          </div>
          <div>
            <h3 className="font-bold text-lg text-slate-900">{flight.airline}</h3>
            <div className="flex items-center space-x-2 text-sm text-slate-600">
              <span className="flex items-center">
                <Star className="w-4 h-4 fill-yellow-400 text-yellow-400 mr-1" />
                {flight.rating}
              </span>
              <span>•</span>
              <span>{flight.class}</span>
              <span>•</span>
              <span className="flex items-center">
                {flight.stops === 0 ? (
                  <span className="text-green-600 font-medium">Non-stop</span>
                ) : (
                  <span>{flight.stops} stop{flight.stops > 1 ? 's' : ''}</span>
                )}
              </span>
            </div>
          </div>
        </div>

        {/* Route Info */}
        <div className="flex items-center space-x-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-slate-900">{flight.departure}</div>
            <div className="text-sm text-slate-600 font-medium">{flight.from}</div>
          </div>

          <div className="flex-1 flex flex-col items-center">
            <div className="flex items-center space-x-1 text-slate-500 mb-1">
              <Clock size={14} />
              <span className="text-xs font-medium">{flight.duration}</span>
            </div>
            <div className="w-full h-0.5 bg-slate-200 relative">
              <div className="absolute left-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-slate-600 rounded-full"></div>
              <div className="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-slate-600 rounded-full"></div>
            </div>
          </div>

          <div className="text-center">
            <div className="text-2xl font-bold text-slate-900">{flight.arrival}</div>
            <div className="text-sm text-slate-600 font-medium">{flight.to}</div>
          </div>
        </div>
      </div>

      {/* Price and Action */}
      <div className="flex md:flex-col items-center md:items-end justify-between md:justify-center gap-4">
        <div className="text-right">
          <div className="flex items-center text-slate-600 text-sm mb-1">
            <DollarSign size={14} />
            <span>from</span>
          </div>
          <div className="text-3xl font-bold text-slate-800">${flight.price}</div>
          <div className="text-xs text-slate-500">per person</div>
        </div>
        <button className="btn-primary px-6 py-3 whitespace-nowrap group">
          <span>Select Flight</span>
          <ArrowRight size={16} className="ml-2 inline group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  </div>
);

export default FlightsPage;
