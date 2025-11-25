import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 justify-items-center md:justify-items-start">
          <div className="col-span-2 md:col-span-1 text-center md:text-left">
            <h3 className="text-lg font-semibold text-slate-900 mb-3">KAYAK</h3>
            <p className="text-sm text-slate-600 leading-relaxed max-w-xs mx-auto md:mx-0">
              A distributed systems project demonstrating travel booking platform architecture.
            </p>
          </div>
          <div className="text-center md:text-left">
            <h4 className="text-sm font-semibold text-slate-900 mb-3">Services</h4>
            <ul className="space-y-2.5">
              <li>
                <Link to="/flights" className="text-sm text-slate-600 hover:text-slate-900 transition-colors">
                  Flights
                </Link>
              </li>
              <li>
                <Link to="/hotels" className="text-sm text-slate-600 hover:text-slate-900 transition-colors">
                  Hotels
                </Link>
              </li>
              <li>
                <Link to="/cars" className="text-sm text-slate-600 hover:text-slate-900 transition-colors">
                  Car Rentals
                </Link>
              </li>
            </ul>
          </div>
          <div className="text-center md:text-left">
            <h4 className="text-sm font-semibold text-slate-900 mb-3">Company</h4>
            <ul className="space-y-2.5">
              <li>
                <a href="#" className="text-sm text-slate-600 hover:text-slate-900 transition-colors">
                  About Us
                </a>
              </li>
              <li>
                <a href="#" className="text-sm text-slate-600 hover:text-slate-900 transition-colors">
                  Careers
                </a>
              </li>
              <li>
                <a href="#" className="text-sm text-slate-600 hover:text-slate-900 transition-colors">
                  Press
                </a>
              </li>
            </ul>
          </div>
          <div className="text-center md:text-left">
            <h4 className="text-sm font-semibold text-slate-900 mb-3">Support</h4>
            <ul className="space-y-2.5">
              <li>
                <a href="#" className="text-sm text-slate-600 hover:text-slate-900 transition-colors">
                  Help Center
                </a>
              </li>
              <li>
                <a href="#" className="text-sm text-slate-600 hover:text-slate-900 transition-colors">
                  Contact Us
                </a>
              </li>
              <li>
                <a href="#" className="text-sm text-slate-600 hover:text-slate-900 transition-colors">
                  Privacy Policy
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className="border-t border-slate-200 mt-12 pt-8">
          <p className="text-center text-sm text-slate-500">
            © 2025 Kayak Simulation - Distributed Systems Group Project
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

