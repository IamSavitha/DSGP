import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plane, Hotel, Car, Search, Calendar, Users, MapPin, TrendingDown, Sparkles, Bell } from 'lucide-react';

type SearchType = 'flights' | 'hotels' | 'cars';

const HomePage: React.FC = () => {
  const [searchType, setSearchType] = useState<SearchType>('flights');
  const navigate = useNavigate();
  
  return (
    <div className="relative">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-br from-slate-50 via-blue-50/30 to-slate-50 border-b border-slate-200 overflow-hidden">
        {/* Decorative background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-200/20 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-slate-200/20 rounded-full blur-3xl"></div>
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28 relative z-10">
          <div className="text-center mb-14">
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-slate-900 mb-6 tracking-tight">
              Compare and Save on{' '}
              <span className="bg-gradient-to-r from-blue-600 to-slate-900 bg-clip-text text-transparent">
                Travel
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
              Search hundreds of travel sites at once to find the best deals
            </p>
          </div>
          
          {/* Search Tabs */}
          <div className="flex justify-center mb-10">
            <div className="inline-flex bg-white/80 backdrop-blur-sm border border-slate-200 rounded-xl p-1.5 shadow-lg">
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
              icon={<TrendingDown className="text-slate-900" size={24} />}
            />
            <FeatureCard
              title="AI-Powered Recommendations"
              description="Our smart concierge finds personalized deals and bundles just for you."
              icon={<Sparkles className="text-slate-900" size={24} />}
            />
            <FeatureCard
              title="Price Alerts"
              description="Set alerts and we'll notify you when prices drop for your dream trip."
              icon={<Bell className="text-slate-900" size={24} />}
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
    className={`flex items-center space-x-2 px-6 py-3 rounded-lg text-sm font-semibold transition-all duration-200 ${
      active
        ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-md shadow-blue-500/20 scale-105'
        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
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
    <div className="bg-white/95 backdrop-blur-sm rounded-2xl border border-slate-200/80 shadow-xl p-6 md:p-8 transform hover:shadow-2xl transition-shadow duration-300 mx-auto">
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider">From</label>
          <div className="flex items-center border-2 border-slate-200 rounded-xl px-4 py-3 bg-slate-50/50 focus-within:border-blue-500 focus-within:bg-white focus-within:ring-2 focus-within:ring-blue-500/20 transition-all">
            <MapPin className="text-slate-500 mr-3 flex-shrink-0" size={18} />
            <input
              type="text"
              placeholder="City or airport"
              className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent"
            />
          </div>
        </div>
        
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider">To</label>
          <div className="flex items-center border-2 border-slate-200 rounded-xl px-4 py-3 bg-slate-50/50 focus-within:border-blue-500 focus-within:bg-white focus-within:ring-2 focus-within:ring-blue-500/20 transition-all">
            <MapPin className="text-slate-500 mr-3 flex-shrink-0" size={18} />
            <input
              type="text"
              placeholder="City or airport"
              className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent"
            />
          </div>
        </div>
        
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider">Dates</label>
          <div className="flex items-center border-2 border-slate-200 rounded-xl px-4 py-3 bg-slate-50/50 focus-within:border-blue-500 focus-within:bg-white focus-within:ring-2 focus-within:ring-blue-500/20 transition-all">
            <Calendar className="text-slate-500 mr-3 flex-shrink-0" size={18} />
            <input
              type="text"
              placeholder="Add dates"
              className="w-full outline-none text-sm font-semibold text-slate-900 placeholder:text-slate-400 bg-transparent"
            />
          </div>
        </div>
        
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider">Travelers</label>
          <div className="flex items-center border-2 border-slate-200 rounded-xl px-4 py-3 bg-slate-50/50 focus-within:border-blue-500 focus-within:bg-white focus-within:ring-2 focus-within:ring-blue-500/20 transition-all">
            <Users className="text-slate-500 mr-3 flex-shrink-0" size={18} />
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
        className="w-full mt-8 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold py-4 px-6 rounded-xl flex items-center justify-center space-x-2 transition-all duration-200 shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40 hover:scale-[1.02] active:scale-[0.98]"
      >
        <Search size={20} />
        <span className="text-base">Search</span>
      </button>
    </div>
  );
};

interface FeatureCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ title, description, icon }) => (
  <div className="text-center group p-6 rounded-2xl hover:bg-slate-50 transition-all duration-300 hover:scale-105">
    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-50 to-slate-100 mb-5 group-hover:from-blue-100 group-hover:to-blue-50 transition-all duration-300 shadow-sm">
      {icon}
    </div>
    <h3 className="text-xl font-bold mb-3 text-slate-900">{title}</h3>
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
  <div className="group cursor-pointer">
    <div className="relative overflow-hidden rounded-2xl aspect-[4/3] border-2 border-slate-200 bg-gradient-to-br from-slate-300 to-slate-400 shadow-md group-hover:shadow-xl transition-all duration-300 group-hover:border-blue-300">
      <div
        className="absolute inset-0 bg-cover bg-center transform group-hover:scale-110 transition-transform duration-700"
        style={{ backgroundImage: `url(${image})`, backgroundColor: '#64748b' }}
      />
      <div className="absolute inset-0 bg-gradient-to-t from-slate-900/90 via-slate-900/40 to-slate-900/20 group-hover:from-slate-900/95 transition-all duration-300" />
      <div className="absolute bottom-0 left-0 right-0 p-5 text-white">
        <h3 className="text-xl font-bold mb-1 group-hover:translate-y-[-2px] transition-transform">{city}</h3>
        <p className="text-sm text-slate-200 font-medium">{country}</p>
      </div>
      <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-md text-slate-900 px-4 py-2 rounded-xl text-sm font-bold shadow-lg group-hover:scale-110 transition-transform">
        from ${price}
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

