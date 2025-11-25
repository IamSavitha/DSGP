import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Plane, Hotel, Car, User, LayoutDashboard, Menu, X } from 'lucide-react';

const Navbar: React.FC = () => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  const isActive = (path: string) => location.pathname === path;
  
  return (
    <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200/80 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-center items-center h-16 relative">
          {/* Logo - Centered */}
          <Link to="/" className="absolute left-0 flex items-center space-x-2 group">
            <span className="text-xl font-bold text-slate-900 tracking-tight group-hover:text-blue-600 transition-colors">
              KAYAK
            </span>
            <span className="text-xs text-slate-500 font-normal">Simulation</span>
          </Link>
          
          {/* Desktop Navigation Links - Centered */}
          <div className="hidden md:flex items-center justify-center space-x-1 mx-auto">
            <NavLink to="/flights" icon={<Plane size={16} />} active={isActive('/flights')}>
              Flights
            </NavLink>
            <NavLink to="/hotels" icon={<Hotel size={16} />} active={isActive('/hotels')}>
              Hotels
            </NavLink>
            <NavLink to="/cars" icon={<Car size={16} />} active={isActive('/cars')}>
              Cars
            </NavLink>
          </div>
          
          {/* Desktop User Menu - Right Aligned */}
          <div className="hidden md:flex items-center space-x-6 absolute right-0">
            <Link
              to="/bookings"
              className="text-sm text-slate-600 hover:text-slate-900 transition-colors font-medium"
            >
              My Trips
            </Link>
            <Link
              to="/admin"
              className="flex items-center space-x-1.5 text-sm text-slate-600 hover:text-slate-900 transition-colors"
            >
              <LayoutDashboard size={16} />
              <span>Admin</span>
            </Link>
            <Link
              to="/login"
              className="flex items-center space-x-1.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:from-blue-700 hover:to-blue-800 transition-all shadow-sm hover:shadow-md"
            >
              <User size={16} />
              <span>Sign In</span>
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 text-slate-600 hover:text-slate-900"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-slate-200">
            <div className="flex flex-col items-center space-y-3">
              <MobileNavLink to="/flights" icon={<Plane size={18} />} active={isActive('/flights')} onClick={() => setMobileMenuOpen(false)}>
                Flights
              </MobileNavLink>
              <MobileNavLink to="/hotels" icon={<Hotel size={18} />} active={isActive('/hotels')} onClick={() => setMobileMenuOpen(false)}>
                Hotels
              </MobileNavLink>
              <MobileNavLink to="/cars" icon={<Car size={18} />} active={isActive('/cars')} onClick={() => setMobileMenuOpen(false)}>
                Cars
              </MobileNavLink>
              <div className="pt-3 border-t border-slate-200 space-y-3 w-full flex flex-col items-center">
                <Link to="/bookings" className="block text-slate-600 hover:text-slate-900 font-medium text-center" onClick={() => setMobileMenuOpen(false)}>
                  My Trips
                </Link>
                <Link to="/admin" className="flex items-center space-x-2 text-slate-600 hover:text-slate-900" onClick={() => setMobileMenuOpen(false)}>
                  <LayoutDashboard size={18} />
                  <span>Admin</span>
                </Link>
                <Link to="/login" className="flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-4 py-2 rounded-lg font-medium" onClick={() => setMobileMenuOpen(false)}>
                  <User size={18} />
                  <span>Sign In</span>
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

interface NavLinkProps {
  to: string;
  icon: React.ReactNode;
  active: boolean;
  children: React.ReactNode;
}

const NavLink: React.FC<NavLinkProps> = ({ to, icon, active, children }) => (
  <Link
    to={to}
    className={`flex items-center space-x-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
      active
        ? 'text-slate-900 bg-slate-100'
        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
    }`}
  >
    {icon}
    <span>{children}</span>
  </Link>
);

interface MobileNavLinkProps {
  to: string;
  icon: React.ReactNode;
  active: boolean;
  children: React.ReactNode;
  onClick: () => void;
}

const MobileNavLink: React.FC<MobileNavLinkProps> = ({ to, icon, active, children, onClick }) => (
  <Link
    to={to}
    onClick={onClick}
    className={`flex items-center space-x-2 px-3 py-2 rounded-md font-medium transition-colors ${
      active
        ? 'text-slate-900 bg-slate-100'
        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
    }`}
  >
    {icon}
    <span>{children}</span>
  </Link>
);

export default Navbar;

