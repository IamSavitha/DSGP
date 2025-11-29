import React, { useState } from 'react';
import { Car, MapPin, Calendar, Search, Filter, Star, Users, Fuel, Gauge, ArrowRight, DollarSign, Luggage } from 'lucide-react';

interface CarRental {
  id: string;
  name: string;
  company: string;
  type: string;
  transmission: string;
  passengers: number;
  luggage: number;
  fuelType: string;
  price: number;
  rating: number;
  reviews: number;
  image: string;
  features: string[];
}

const CarsPage: React.FC = () => {
  const [showFilters, setShowFilters] = useState(false);

  // Mock car rental data
  const cars: CarRental[] = [
    {
      id: '1',
      name: 'Toyota Camry',
      company: 'Enterprise',
      type: 'Sedan',
      transmission: 'Automatic',
      passengers: 5,
      luggage: 3,
      fuelType: 'Gasoline',
      price: 45,
      rating: 4.7,
      reviews: 524,
      image: '/images/car1.jpg',
      features: ['GPS', 'Bluetooth', 'USB Ports']
    },
    {
      id: '2',
      name: 'Honda CR-V',
      company: 'Hertz',
      type: 'SUV',
      transmission: 'Automatic',
      passengers: 7,
      luggage: 4,
      fuelType: 'Gasoline',
      price: 65,
      rating: 4.8,
      reviews: 892,
      image: '/images/car2.jpg',
      features: ['GPS', 'Bluetooth', 'Backup Camera', 'USB Ports']
    },
    {
      id: '3',
      name: 'Tesla Model 3',
      company: 'Hertz',
      type: 'Luxury Sedan',
      transmission: 'Automatic',
      passengers: 5,
      luggage: 2,
      fuelType: 'Electric',
      price: 95,
      rating: 4.9,
      reviews: 1240,
      image: '/images/car3.jpg',
      features: ['Autopilot', 'Premium Sound', 'GPS', 'USB Ports']
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100/30">
      {/* Search Header */}
      <div className="bg-gradient-to-r from-slate-700 to-slate-800 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-8 animate-slide-down">Rent a Car</h1>

          {/* Search Form */}
          <div className="glass rounded-2xl p-6 border-2 border-white/20 shadow-2xl animate-scale-in">
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider">Pick-up Location</label>
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
                <label className="text-xs font-bold uppercase tracking-wider">Pick-up Date</label>
                <div className="flex items-center border-2 border-white/30 rounded-xl px-4 py-3 bg-white/10 focus-within:border-white focus-within:bg-white/20 transition-all">
                  <Calendar className="text-white mr-3 flex-shrink-0" size={18} />
                  <input
                    type="date"
                    className="w-full outline-none text-sm font-semibold text-white placeholder:text-white/60 bg-transparent"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider">Drop-off Date</label>
                <div className="flex items-center border-2 border-white/30 rounded-xl px-4 py-3 bg-white/10 focus-within:border-white focus-within:bg-white/20 transition-all">
                  <Calendar className="text-white mr-3 flex-shrink-0" size={18} />
                  <input
                    type="date"
                    className="w-full outline-none text-sm font-semibold text-white placeholder:text-white/60 bg-transparent"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider">Car Type</label>
                <div className="flex items-center border-2 border-white/30 rounded-xl px-4 py-3 bg-white/10 focus-within:border-white focus-within:bg-white/20 transition-all">
                  <Car className="text-white mr-3 flex-shrink-0" size={18} />
                  <select className="w-full outline-none text-sm font-semibold text-white bg-transparent appearance-none">
                    <option value="" className="bg-blue-600">All Types</option>
                    <option value="sedan" className="bg-blue-600">Sedan</option>
                    <option value="suv" className="bg-blue-600">SUV</option>
                    <option value="luxury" className="bg-blue-600">Luxury</option>
                  </select>
                </div>
              </div>
            </div>

            <button className="w-full mt-6 bg-white text-slate-800 hover:bg-slate-50 font-bold py-4 px-6 rounded-xl flex items-center justify-center space-x-3 transition-all duration-200 shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98] group">
              <Search size={20} className="group-hover:rotate-90 transition-transform duration-300" />
              <span className="text-base">Search Cars</span>
              <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform duration-300" />
            </button>
          </div>
        </div>
      </div>

      {/* Results Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-3xl font-bold text-slate-900">Available Cars</h2>
            <p className="text-slate-600 mt-1">{cars.length} vehicles found</p>
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
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Price Per Day</h4>
                  <input type="range" min="0" max="200" className="w-full" />
                  <div className="flex justify-between text-xs text-slate-600 mt-2">
                    <span>$0</span>
                    <span>$200+</span>
                  </div>
                </div>

                {/* Car Type */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Car Type</h4>
                  <div className="space-y-2">
                    {['Sedan', 'SUV', 'Luxury', 'Compact'].map((type) => (
                      <label key={type} className="flex items-center space-x-2 cursor-pointer group">
                        <input type="checkbox" className="rounded text-blue-600 focus:ring-blue-500" />
                        <span className="text-sm text-slate-600 group-hover:text-slate-900">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Transmission */}
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Transmission</h4>
                  <div className="space-y-2">
                    {['Automatic', 'Manual'].map((trans) => (
                      <label key={trans} className="flex items-center space-x-2 cursor-pointer group">
                        <input type="checkbox" className="rounded text-blue-600 focus:ring-blue-500" />
                        <span className="text-sm text-slate-600 group-hover:text-slate-900">{trans}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Fuel Type */}
                <div>
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Fuel Type</h4>
                  <div className="space-y-2">
                    {['Gasoline', 'Electric', 'Hybrid'].map((fuel) => (
                      <label key={fuel} className="flex items-center space-x-2 cursor-pointer group">
                        <input type="checkbox" className="rounded text-blue-600 focus:ring-blue-500" />
                        <span className="text-sm text-slate-600 group-hover:text-slate-900">{fuel}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Car Results */}
          <div className={showFilters ? 'lg:col-span-2' : 'lg:col-span-3'}>
            <div className="grid md:grid-cols-2 gap-6">
              {cars.map((car, index) => (
                <CarCard key={car.id} car={car} delay={index * 100} />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

interface CarCardProps {
  car: CarRental;
  delay: number;
}

const CarCard: React.FC<CarCardProps> = ({ car, delay }) => (
  <div
    className="card-interactive p-0 overflow-hidden animate-slide-up"
    style={{ animationDelay: `${delay}ms` }}
  >
    {/* Car Image */}
    <div className="relative aspect-[16/10] bg-gradient-to-br from-slate-300 to-slate-400">
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{ backgroundImage: `url(${car.image})`, backgroundColor: '#64748b' }}
      />
      <div className="absolute top-4 left-4 bg-slate-700 text-white px-3 py-1.5 rounded-lg text-xs font-bold uppercase">
        {car.type}
      </div>
      <div className="absolute top-4 right-4 glass px-3 py-1.5 rounded-lg text-sm font-bold text-slate-900">
        <Star className="w-4 h-4 inline fill-yellow-400 text-yellow-400 mr-1" />
        {car.rating}
      </div>
    </div>

    {/* Car Info */}
    <div className="p-6">
      <div className="mb-4">
        <h3 className="text-xl font-bold text-slate-900 mb-1">{car.name}</h3>
        <div className="flex items-center text-sm text-slate-600">
          <span className="font-medium">{car.company}</span>
          <span className="mx-2">•</span>
          <span className="flex items-center">
            <Star className="w-3 h-3 fill-yellow-400 text-yellow-400 mr-1" />
            ({car.reviews} reviews)
          </span>
        </div>
      </div>

      {/* Specs */}
      <div className="grid grid-cols-2 gap-3 mb-4 pb-4 border-b border-slate-200">
        <div className="flex items-center text-sm text-slate-600">
          <Users size={16} className="mr-2 text-slate-600" />
          <span>{car.passengers} passengers</span>
        </div>
        <div className="flex items-center text-sm text-slate-600">
          <Luggage size={16} className="mr-2 text-slate-600" />
          <span>{car.luggage} bags</span>
        </div>
        <div className="flex items-center text-sm text-slate-600">
          <Gauge size={16} className="mr-2 text-slate-600" />
          <span>{car.transmission}</span>
        </div>
        <div className="flex items-center text-sm text-slate-600">
          <Fuel size={16} className="mr-2 text-slate-600" />
          <span>{car.fuelType}</span>
        </div>
      </div>

      {/* Features */}
      <div className="mb-4">
        <div className="flex flex-wrap gap-2">
          {car.features.map((feature) => (
            <span
              key={feature}
              className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-700"
            >
              {feature}
            </span>
          ))}
        </div>
      </div>

      {/* Price and Action */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-200">
        <div>
          <div className="flex items-center text-slate-600 text-xs mb-1">
            <DollarSign size={12} />
            <span>per day</span>
          </div>
          <div className="text-2xl font-bold text-slate-800">${car.price}</div>
        </div>
        <button className="btn-primary px-5 py-2.5 text-sm whitespace-nowrap group">
          <span>Reserve</span>
          <ArrowRight size={14} className="ml-2 inline group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  </div>
);

export default CarsPage;
