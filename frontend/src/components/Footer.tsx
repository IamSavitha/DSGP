import React from 'react';
import { Link } from 'react-router-dom';
import { Plane, Hotel, Car, Mail, Github, Linkedin, Twitter, ExternalLink } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white border-t border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-12 justify-items-center md:justify-items-start mb-12">
          {/* Brand Section */}
          <div className="col-span-2 md:col-span-1 text-center md:text-left">
            <div className="mb-4">
              <h3 className="text-3xl font-black gradient-text mb-2">KAYAK</h3>
              <span className="text-xs text-slate-400 font-medium bg-slate-800 px-2 py-1 rounded">Distributed Systems Project</span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed max-w-xs mx-auto md:mx-0 mb-6">
              A modern travel booking platform demonstrating microservices architecture with AI-powered recommendations.
            </p>
            {/* Social Links */}
            <div className="flex space-x-3 justify-center md:justify-start">
              <a href="#" className="p-2 rounded-lg bg-slate-800 hover:bg-blue-600 transition-all duration-300 hover:scale-110 group">
                <Github size={18} className="text-slate-400 group-hover:text-white transition-colors" />
              </a>
              <a href="#" className="p-2 rounded-lg bg-slate-800 hover:bg-blue-600 transition-all duration-300 hover:scale-110 group">
                <Twitter size={18} className="text-slate-400 group-hover:text-white transition-colors" />
              </a>
              <a href="#" className="p-2 rounded-lg bg-slate-800 hover:bg-blue-600 transition-all duration-300 hover:scale-110 group">
                <Linkedin size={18} className="text-slate-400 group-hover:text-white transition-colors" />
              </a>
            </div>
          </div>
          {/* Services */}
          <div className="text-center md:text-left">
            <h4 className="text-sm font-bold text-white mb-4 uppercase tracking-wider">Services</h4>
            <ul className="space-y-3">
              <li>
                <Link to="/flights" className="text-sm text-slate-400 hover:text-white transition-colors flex items-center justify-center md:justify-start group">
                  <Plane size={16} className="mr-2 group-hover:translate-x-1 transition-transform" />
                  <span>Flights</span>
                </Link>
              </li>
              <li>
                <Link to="/hotels" className="text-sm text-slate-400 hover:text-white transition-colors flex items-center justify-center md:justify-start group">
                  <Hotel size={16} className="mr-2 group-hover:translate-x-1 transition-transform" />
                  <span>Hotels</span>
                </Link>
              </li>
              <li>
                <Link to="/cars" className="text-sm text-slate-400 hover:text-white transition-colors flex items-center justify-center md:justify-start group">
                  <Car size={16} className="mr-2 group-hover:translate-x-1 transition-transform" />
                  <span>Car Rentals</span>
                </Link>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div className="text-center md:text-left">
            <h4 className="text-sm font-bold text-white mb-4 uppercase tracking-wider">Company</h4>
            <ul className="space-y-3">
              <li>
                <a href="#" className="text-sm text-slate-400 hover:text-white transition-colors inline-flex items-center group">
                  <span>About Us</span>
                  <ExternalLink size={14} className="ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
                </a>
              </li>
              <li>
                <a href="#" className="text-sm text-slate-400 hover:text-white transition-colors inline-flex items-center group">
                  <span>Careers</span>
                  <ExternalLink size={14} className="ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
                </a>
              </li>
              <li>
                <a href="#" className="text-sm text-slate-400 hover:text-white transition-colors inline-flex items-center group">
                  <span>Press</span>
                  <ExternalLink size={14} className="ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
                </a>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div className="text-center md:text-left">
            <h4 className="text-sm font-bold text-white mb-4 uppercase tracking-wider">Support</h4>
            <ul className="space-y-3">
              <li>
                <a href="#" className="text-sm text-slate-400 hover:text-white transition-colors">
                  Help Center
                </a>
              </li>
              <li>
                <a href="#" className="text-sm text-slate-400 hover:text-white transition-colors flex items-center justify-center md:justify-start group">
                  <Mail size={16} className="mr-2 group-hover:scale-110 transition-transform" />
                  <span>Contact Us</span>
                </a>
              </li>
              <li>
                <a href="#" className="text-sm text-slate-400 hover:text-white transition-colors">
                  Privacy Policy
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t border-slate-700 mt-12 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <p className="text-sm text-slate-400">
              © 2025 Kayak Simulation - Distributed Systems Group Project
            </p>
            <div className="flex items-center space-x-6 text-sm text-slate-400">
              <a href="#" className="hover:text-white transition-colors">Terms</a>
              <a href="#" className="hover:text-white transition-colors">Privacy</a>
              <a href="#" className="hover:text-white transition-colors">Cookies</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;

