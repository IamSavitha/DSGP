import React, { useState } from 'react';
import { Hotel, MapPin, Calendar, Users, Search, Filter, Star, Wifi, Coffee, ParkingSquare, ArrowRight, DollarSign } from 'lucide-react';

interface HotelListing {
  id: string;
  name: string;
  location: string;
  rating: number;
  reviews: number;
  price: number;
  image: string;
  amenities: string[];
  roomType: string;
}

const HotelsPage: React.FC = () => {
  const [showFilters, setShowFilters] = useState(false);

  // Mock hotel data
  const hotels: HotelListing[] = [
    {
      id: '1',
      name: 'Grand Plaza Hotel',
      location: 'Downtown Los Angeles',
      rating: 4.8,
      reviews: 1240,
      price: 189,
      image: '/images/hotel1.jpg',
      amenities: ['WiFi', 'Pool', 'Parking', 'Breakfast'],
      roomType: 'Deluxe King Room'
    },
    {
      id: '2',
      name: 'Sunset Beach Resort',
      location: 'Santa Monica',
      rating: 4.6,
      reviews: 856,
      price: 249,
      image: '/images/hotel2.jpg',
      amenities: ['WiFi', 'Pool', 'Spa', 'Restaurant'],
      roomType: 'Ocean View Suite'
    },
    {
      id: '3',
      name: 'City Center Inn',
      location: 'Downtown LA',
      rating: 4.3,
      reviews: 642,
      price: 129,
      image: '/images/hotel3.jpg',
      amenities: ['WiFi', 'Parking', 'Breakfast'],
      roomType: 'Standard Double Room'
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30">
      {/* Search Header */}
      <div className="bg-gradient-to-r from-slate-700 to-slate-800 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-8 animate-slide-down">Find Your Perfect Stay</h1>

          {/* Search Form */}
          <div className="glass rounded-2xl p-6 border-2 border-white/20 shadow-2xl animate-scale-in">
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider">Destination</label>
                <div className="flex items-center border-2 border-white/30 rounded-xl px-4 py-3 bg-white/10 focus-within:border-white focus-within:bg-white/20 transition-all">
                  <MapPin className="text-white mr-3 flex-shrink-0" size={18} />
                  <input
                    type="text"
                    placeholder="Los Angeles, CA"
                    className="w-full outline-none text-sm font-semibold text-white placeholder:text-white/60 bg-transparent"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider">Check-in</label>
                <div className="flex items-center border-2 border-white/30 rounded-xl px-4 py-3 bg-white/10 focus-within:border-white focus-within:bg-white/20 transition-all">
                  <Calendar className="text-white mr-3 flex-shrink-0" size={18} />
                  <input
                    type="date"
                    className="w-full outline-none text-sm font-semibold text-white placeholder:text-white/60 bg-transparent"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider">Check-out</label>
                <div className="flex items-center border-2 border-white/30 rounded-xl px-4 py-3 bg-white/10 focus-within:border-white focus-within:bg-white/20 transition-all">
                  <Calendar className="text-white mr-3 flex-shrink-0" size={18} />
                  <input
                    type="date"
                    className="w-full outline-none text-sm font-semibold text-white placeholder:text-white/60 bg-transparent"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider">Guests</label>
                <div className="flex items-center border-2 border-white/30 rounded-xl px-4 py-3 bg-white/10 focus-within:border-white focus-within:bg-white/20 transition-all">
                  <Users className="text-white mr-3 flex-shrink-0" size={18} />
                  <input
                    type="number"
                    placeholder="2"
                    min="1"
                    className="w-full outline-none text-sm font-semibold text-white placeholder:text-white/60 bg-transparent"
                  />
                </div>
              </div>
            </div>

            <button className="w-full mt-6 bg-white text-slate-800 hover:bg-slate-50 font-bold py-4 px-6 rounded-xl flex items-center justify-center space-x-3 transition-all duration-200 shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] group">
              <Search size={20} className="group-hover:rotate-90 transition-transform duration-300" />
              <span className="text-base">Search Hotels</span>
              <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform duration-300" />
            </button>
          </div>
        </div>
      </div>

      {/* Results Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold text-slate-900">Available Hotels</h2>
            <p className="text-slate-600 mt-1">{hotels.length} properties found</p>
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

                {/* Price Range */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Price Range</h4>
                  <input type="range" min="0" max="500" className="w-full" />
                  <div className="flex justify-between text-xs text-slate-600 mt-2">
                    <span>$0</span>
                    <span>$500+</span>
                  </div>
                </div>

                {/* Star Rating */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Star Rating</h4>
                  <div className="space-y-2">
                    {[5, 4, 3, 2].map((stars) => (
                      <label key={stars} className="flex items-center space-x-2 cursor-pointer group">
                        <input type="checkbox" className="rounded text-slate-600 focus:ring-slate-500" />
                        <div className="flex items-center text-sm text-slate-600 group-hover:text-slate-900">
                          {Array.from({ length: stars }).map((_, i) => (
                            <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                          ))}
                          <span className="ml-1">& up</span>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Amenities */}
                <div>
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Amenities</h4>
                  <div className="space-y-2">
                    {[
                      { icon: <Wifi size={16} />, label: 'WiFi' },
                      { icon: <Coffee size={16} />, label: 'Breakfast' },
                      { icon: <ParkingSquare size={16} />, label: 'Parking' }
                    ].map(({ icon, label }) => (
                      <label key={label} className="flex items-center space-x-2 cursor-pointer group">
                        <input type="checkbox" className="rounded text-slate-600 focus:ring-slate-500" />
                        <span className="flex items-center text-sm text-slate-600 group-hover:text-slate-900">
                          {icon}
                          <span className="ml-2">{label}</span>
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Hotel Results */}
          <div className={showFilters ? 'lg:col-span-2' : 'lg:col-span-3'}>
            <div className="space-y-4">
              {hotels.map((hotel, index) => (
                <HotelCard key={hotel.id} hotel={hotel} delay={index * 100} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

interface HotelCardProps {
  hotel: HotelListing;
  delay: number;
}

const HotelCard: React.FC<HotelCardProps> = ({ hotel, delay }) => (
  <div
    className="card-interactive p-0 overflow-hidden animate-slide-up"
    style={{ animationDelay: `${delay}ms` }}
  >
    <div className="grid md:grid-cols-3 gap-0">
      {/* Hotel Image */}
      <div className="md:col-span-1 relative aspect-[4/3] md:aspect-auto bg-gradient-to-br from-slate-300 to-slate-400">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${hotel.image})`, backgroundColor: '#64748b' }}
        />
        <div className="absolute top-4 left-4 glass px-3 py-1.5 rounded-lg text-sm font-bold text-slate-900">
          <Star className="w-4 h-4 inline fill-yellow-400 text-yellow-400 mr-1" />
          {hotel.rating}
        </div>
      </div>

      {/* Hotel Info */}
      <div className="md:col-span-2 p-6 flex flex-col justify-between">
        <div>
          <div className="flex items-start justify-between mb-3">
            <div>
              <h3 className="text-xl font-bold text-slate-900 mb-1">{hotel.name}</h3>
              <div className="flex items-center text-slate-600 text-sm">
                <MapPin size={14} className="mr-1" />
                <span>{hotel.location}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2 mb-4 text-sm">
            <div className="flex">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star
                  key={i}
                  className={`w-4 h-4 ${
                    i < Math.floor(hotel.rating)
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'text-slate-300'
                  }`}
                />
              ))}
            </div>
            <span className="text-slate-600">({hotel.reviews} reviews)</span>
          </div>

          <div className="mb-4">
            <span className="text-sm font-medium text-slate-700">{hotel.roomType}</span>
          </div>

          <div className="flex flex-wrap gap-2">
            {hotel.amenities.map((amenity) => (
              <span
                key={amenity}
                className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200"
              >
                {amenity}
              </span>
            ))}
          </div>
        </div>

        <div className="flex items-end justify-between mt-6 pt-4 border-t border-slate-200">
          <div>
            <div className="flex items-center text-slate-600 text-sm mb-1">
              <DollarSign size={14} />
              <span>per night</span>
            </div>
            <div className="text-3xl font-bold text-slate-800">${hotel.price}</div>
            <div className="text-xs text-slate-500">includes taxes & fees</div>
          </div>
          <button className="btn-primary px-6 py-3 whitespace-nowrap group">
            <span>View Details</span>
            <ArrowRight size={16} className="ml-2 inline group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>
    </div>
  </div>
);

export default HotelsPage;
