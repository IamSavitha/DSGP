import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plane, Hotel, Car, Search, Calendar, Users, MapPin, TrendingDown, Sparkles, Bell, ArrowRight, Star, CheckCircle2, Globe, Package } from 'lucide-react';

type SearchType = 'flights' | 'hotels' | 'cars';

const HomePage: React.FC = () => {
  const [searchType, setSearchType] = useState<SearchType>('flights');
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-br from-slate-50 via-white to-slate-100 border-b border-slate-200 overflow-hidden">
        {/* Decorative background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-slate-300/20 rounded-full blur-3xl animate-pulse-slow"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-slate-300/15 rounded-full blur-3xl animate-pulse-slow animation-delay-400"></div>
          <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-slate-200/15 rounded-full blur-3xl animate-pulse-slow animation-delay-600"></div>
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28 relative z-10">
          {/* Trust Badge */}
          <div className="text-center mb-8 animate-slide-down">
            <div className="inline-flex items-center space-x-2 bg-slate-100 border border-slate-300 text-slate-700 px-4 py-2 rounded-full text-sm font-medium">
              <Star className="w-4 h-4 fill-slate-600 text-slate-600" />
              <span>Trusted by 1M+ travelers worldwide</span>
              <Star className="w-4 h-4 fill-slate-600 text-slate-600" />
            </div>
          </div>

          <div className="text-center mb-14 animate-fade-in">
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-slate-900 mb-6 tracking-tight">
              Compare and Save on{' '}
              <span className="gradient-text animate-shimmer">
                Travel
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
              Search hundreds of travel sites at once to find the best deals
            </p>

            {/* Quick Stats */}
            <div className="flex flex-wrap justify-center gap-6 mt-8 animate-slide-up">
              <div className="flex items-center space-x-2 text-slate-700">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
                <span className="text-sm font-medium">100+ Travel Sites</span>
              </div>
              <div className="flex items-center space-x-2 text-slate-700">
                <Globe className="w-5 h-5 text-slate-600" />
                <span className="text-sm font-medium">Global Coverage</span>
              </div>
              <div className="flex items-center space-x-2 text-slate-700">
                <TrendingDown className="w-5 h-5 text-slate-600" />
                <span className="text-sm font-medium">Best Price Guarantee</span>
              </div>
            </div>
          </div>
          
          {/* Search Tabs */}
          <div className="flex justify-center mb-10 animate-scale-in">
            <div className="inline-flex bg-slate-200 rounded-2xl p-2 shadow-lg border-2 border-slate-300">
              <TabButton
                active={searchType === 'flights'}
                onClick={() => setSearchType('flights')}
                icon={<Plane size={18} />}
              >
                Flights
              </TabButton>
              <TabButton
                active={searchType === 'hotels'}
                onClick={() => setSearchType('hotels')}
                icon={<Hotel size={18} />}
              >
                Hotels
              </TabButton>
              <TabButton
                active={searchType === 'cars'}
                onClick={() => setSearchType('cars')}
                icon={<Car size={18} />}
              >
                Cars
              </TabButton>
            </div>
          </div>
          
          {/* Search Form */}
          <div className="max-w-5xl mx-auto">
            <SearchForm type={searchType} onSearch={() => navigate(`/${searchType}`)} />
          </div>
        </div>
      </div>
      
      {/* Features Section */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-semibold text-slate-900 mb-4 tracking-tight">
              Why Book with Us?
            </h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Everything you need to plan and book your perfect trip
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 lg:gap-12 justify-items-center max-w-5xl mx-auto">
            <FeatureCard
              title="Best Price Guarantee"
              description="We search 100+ sites to find you the best deals on flights, hotels, and cars."
              icon={<TrendingDown />}
            />
            <FeatureCard
              title="AI-Powered Trip Bundles"
              description="Get complete packages: Flight + Hotel + Car combinations with AI-optimized pricing and fit scores."
              icon={<Package />}
              onClick={() => navigate('/bundles')}
            />
            <FeatureCard
              title="AI-Powered Recommendations"
              description="Our smart concierge finds personalized deals and bundles just for you."
              icon={<Sparkles />}
            />
          </div>
        </div>
      </div>
      
      {/* Popular Destinations */}
      <div className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-semibold text-slate-900 mb-4 tracking-tight">
              Popular Destinations
            </h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Discover amazing places to visit around the world
            </p>
          </div>
          
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 justify-items-center max-w-6xl mx-auto">
            {destinations.map((dest) => (
              <DestinationCard key={dest.city} {...dest} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

interface TabButtonProps {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  children: React.ReactNode;
}

const TabButton: React.FC<TabButtonProps> = ({ active, onClick, icon, children }) => (
  <button
    onClick={onClick}
    className={`flex items-center space-x-2 px-6 py-3 rounded-xl text-sm font-bold transition-all duration-300 ${
      active
        ? 'bg-gradient-to-r from-slate-700 to-slate-800 text-white shadow-lg shadow-slate-400/20 scale-105'
        : 'text-slate-700 hover:text-slate-900 hover:bg-white/80'
    }`}
  >
    {icon}
    <span>{children}</span>
  </button>
);

interface SearchFormProps {
  type: SearchType;
  onSearch: () => void;
}

const SearchForm: React.FC<SearchFormProps> = ({ onSearch }) => {
  return (
    <div className="bg-white rounded-2xl border-2 border-slate-300 shadow-2xl p-6 md:p-8 transform hover:shadow-xl transition-all duration-500 mx-auto animate-slide-up">
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">From</label>
          <div className="flex items-center border-2 border-slate-300 rounded-xl px-4 py-3 bg-slate-50 focus-within:border-slate-700 focus-within:bg-white focus-within:ring-4 focus-within:ring-slate-400/20 transition-all duration-200 hover:border-slate-400">
            <MapPin className="text-slate-600 mr-3 flex-shrink-0" size={18} />
            <input
              type="text"
              placeholder="City or airport"
              className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">To</label>
          <div className="flex items-center border-2 border-slate-300 rounded-xl px-4 py-3 bg-slate-50 focus-within:border-slate-700 focus-within:bg-white focus-within:ring-4 focus-within:ring-slate-400/20 transition-all duration-200 hover:border-slate-400">
            <MapPin className="text-slate-600 mr-3 flex-shrink-0" size={18} />
            <input
              type="text"
              placeholder="City or airport"
              className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Dates</label>
          <div className="flex items-center border-2 border-slate-300 rounded-xl px-4 py-3 bg-slate-50 focus-within:border-slate-700 focus-within:bg-white focus-within:ring-4 focus-within:ring-slate-400/20 transition-all duration-200 hover:border-slate-400">
            <Calendar className="text-slate-600 mr-3 flex-shrink-0" size={18} />
            <input
              type="text"
              placeholder="Add dates"
              className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">Travelers</label>
          <div className="flex items-center border-2 border-slate-300 rounded-xl px-4 py-3 bg-slate-50 focus-within:border-slate-700 focus-within:bg-white focus-within:ring-4 focus-within:ring-slate-400/20 transition-all duration-200 hover:border-slate-400">
            <Users className="text-slate-600 mr-3 flex-shrink-0" size={18} />
            <input
              type="text"
              placeholder="1 adult"
              className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent"
            />
          </div>
        </div>
      </div>

      <button
        onClick={onSearch}
        className="btn-primary w-full mt-8 py-4 px-6 flex items-center justify-center space-x-3 group"
      >
        <Search size={20} className="group-hover:rotate-90 transition-transform duration-300" />
        <span className="text-base">Search Now</span>
        <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform duration-300" />
      </button>
    </div>
  );
};

interface FeatureCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  onClick?: () => void;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ title, description, icon, onClick }) => (
  <div 
    onClick={onClick}
    className={`text-center group p-8 rounded-2xl bg-gradient-to-br from-white to-slate-50/50 border-2 border-slate-100 hover:border-slate-300 shadow-md hover:shadow-xl transition-all duration-300 hover:scale-105 animate-fade-in ${onClick ? 'cursor-pointer' : ''}`}
  >
    <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-slate-600 to-slate-700 mb-6 group-hover:from-slate-700 group-hover:to-slate-800 transition-all duration-300 shadow-lg shadow-slate-400/20 group-hover:shadow-xl group-hover:shadow-slate-400/30 group-hover:scale-110 group-hover:rotate-3">
      {React.cloneElement(icon as React.ReactElement, { className: 'text-white', size: 28 })}
    </div>
    <h3 className="text-xl font-bold mb-3 text-slate-900 group-hover:text-slate-700 transition-colors">{title}</h3>
    <p className="text-slate-600 text-sm leading-relaxed max-w-sm mx-auto">{description}</p>
  </div>
);

interface DestinationCardProps {
  city: string;
  country: string;
  image: string;
  price: number;
}

const DestinationCard: React.FC<DestinationCardProps> = ({ city, country, image, price }) => (
  <div className="group cursor-pointer animate-scale-in">
    <div className="relative overflow-hidden rounded-2xl aspect-[4/3] border-2 border-slate-200 bg-gradient-to-br from-slate-300 to-slate-400 shadow-lg group-hover:shadow-2xl transition-all duration-500 group-hover:border-slate-400 group-hover:scale-105">
      <div
        className="absolute inset-0 bg-cover bg-center transform group-hover:scale-125 transition-transform duration-1000"
        style={{ backgroundImage: `url(${image})`, backgroundColor: '#64748b' }}
      />
      <div className="absolute inset-0 bg-gradient-to-t from-slate-900/90 via-slate-900/40 to-transparent group-hover:from-slate-900/95 transition-all duration-500" />

      {/* Overlay Effect */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-700/15 to-slate-800/15"></div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 p-6 text-white transform group-hover:translate-y-[-4px] transition-transform duration-300">
        <h3 className="text-2xl font-bold mb-1 drop-shadow-lg">{city}</h3>
        <p className="text-sm text-slate-100 font-medium flex items-center">
          <Globe className="w-4 h-4 mr-1" />
          {country}
        </p>
      </div>

      <div className="absolute top-4 right-4 glass text-slate-900 px-4 py-2.5 rounded-xl text-sm font-bold shadow-xl group-hover:scale-110 group-hover:shadow-glow transition-all duration-300">
        <div className="flex items-center space-x-1">
          <span className="text-xs text-slate-600">from</span>
          <span className="text-lg text-blue-600">${price}</span>
        </div>
      </div>
    </div>
  </div>
);

const destinations = [
  { city: 'New York', country: 'United States', image: '/images/nyc.jpg', price: 299 },
  { city: 'Miami', country: 'United States', image: '/images/miami.jpg', price: 249 },
  { city: 'Los Angeles', country: 'United States', image: '/images/la.jpg', price: 279 },
  { city: 'San Francisco', country: 'United States', image: '/images/sf.jpg', price: 199 },
];

export default HomePage;

