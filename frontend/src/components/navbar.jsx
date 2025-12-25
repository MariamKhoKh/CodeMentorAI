import { useState } from 'react';

function Navbar({ currentPage, navigateTo, onLogout, userData }) {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    console.log('Searching for:', searchQuery);
    // TODO: Implement search functionality with backend
  };

  return (
    <nav className="bg-zinc-900 border-b border-green-500/30 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center">
          <svg className="w-8 h-8 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
          <span className="text-2xl font-bold text-green-500">CodeMentor</span>
        </div>

        {/* Navigation Links */}
        <div className="flex items-center space-x-6">
          <button
            onClick={() => navigateTo('dashboard')}
            className={`text-sm font-semibold transition duration-200 ${
              currentPage === 'dashboard'
                ? 'text-green-500'
                : 'text-gray-400 hover:text-green-400'
            }`}
          >
            Home
          </button>
          
          <button
            onClick={() => console.log('Navigate to profile')}
            className="text-gray-400 hover:text-green-400 text-sm font-semibold transition duration-200"
          >
            Profile
          </button>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="flex-1 max-w-md mx-8">
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search problems..."
              className="w-full px-4 py-2 pl-10 bg-black border border-green-500/30 text-green-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent placeholder-gray-600 text-sm"
            />
            <svg
              className="w-5 h-5 text-gray-500 absolute left-3 top-1/2 transform -translate-y-1/2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </form>

        {/* User Info & Logout */}
        <div className="flex items-center space-x-4">
          {userData && (
            <span className="text-gray-400 text-sm">
              Welcome, <span className="text-green-500 font-semibold">{userData.username}</span>
            </span>
          )}
          <button
            onClick={onLogout}
            className="px-4 py-2 bg-zinc-800 border border-green-500/30 text-green-500 rounded-lg hover:bg-zinc-700 transition duration-200 text-sm font-semibold"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
