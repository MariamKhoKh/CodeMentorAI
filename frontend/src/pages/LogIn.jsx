import { useState } from 'react';

function LogIn({ navigateTo, onLogin }) {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleLogIn = async (e) => {
    e.preventDefault(); // Prevent default form submission
    setError(null);
    setLoading(true);

    try {
      // OAuth2 form format (your backend expects this)
      const formBody = new URLSearchParams();
      formBody.append('username', formData.email); // OAuth2 uses 'username' field for email
      formBody.append('password', formData.password);

      const response = await fetch('http://localhost:8001/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formBody.toString()
      });

      if (!response.ok) {
        let errMsg = 'Login failed';
        try {
          const errData = await response.json();
          if (errData.detail) {
            if (Array.isArray(errData.detail)) {
              errMsg = errData.detail.map(e => e.msg || JSON.stringify(e)).join(', ');
            } else if (typeof errData.detail === 'string') {
              errMsg = errData.detail;
            } else {
              errMsg = JSON.stringify(errData.detail);
            }
          } else {
            errMsg = JSON.stringify(errData);
          }
        } catch (e) {
          errMsg = 'Login failed (invalid error response)';
        }
        throw new Error(errMsg);
      }

      const data = await response.json();
      // Backend returns: { access_token: "...", token_type: "bearer" }
      
      // IMPORTANT: Store token in localStorage
      localStorage.setItem('token', data.access_token);

      // Get user info with the token
      const userResponse = await fetch('http://localhost:8001/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${data.access_token}`
        }
      });

      let userData = {
        email: formData.email,
        token: data.access_token
      };

      if (userResponse.ok) {
        const userInfo = await userResponse.json();
        userData = {
          ...userData,
          ...userInfo // id, username, email, is_active, created_at
        };
      }

      onLogin(userData);

    } catch (err) {
      console.error('Login error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="bg-zinc-900 border border-green-500/30 rounded-lg shadow-2xl shadow-green-500/20 p-8 w-full max-w-md">
        <div className="mb-6 text-center">
          <div className="inline-block mb-3">
            <div className="w-16 h-16 mx-auto bg-green-500/10 rounded-full flex items-center justify-center border border-green-500/30">
              <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
            </div>
          </div>
          <h2 className="text-3xl font-bold text-green-500 mb-2">Log In</h2>
          <p className="text-gray-400 text-sm">Access your CodeMentor account</p>
        </div>

        {error && (
          <div className="mb-4 bg-red-500/10 border border-red-500/30 rounded-lg p-3">
            <p className="text-red-400 text-sm">Error: {error}</p>
          </div>
        )}

        <form onSubmit={handleLogIn} className="space-y-4">
          <div>
            <label className="block text-green-400 text-sm font-semibold mb-2">
              Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              required
              className="w-full px-4 py-2 bg-black border border-green-500/30 text-green-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent placeholder-gray-600"
              placeholder="Enter your email"
            />
          </div>

          <div>
            <label className="block text-green-400 text-sm font-semibold mb-2">
              Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              required
              className="w-full px-4 py-2 bg-black border border-green-500/30 text-green-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent placeholder-gray-600"
              placeholder="Enter your password"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-2 rounded-lg font-bold transition duration-200 shadow-lg ${
              loading
                ? 'bg-gray-600 text-gray-300 cursor-not-allowed'
                : 'bg-green-600 text-black hover:bg-green-500 shadow-green-500/30'
            }`}
          >
            {loading ? 'Logging in...' : 'Log In'}
          </button>
        </form>

        <p className="text-center text-gray-400 mt-6 text-sm">
          Don't have an account?{' '}
          <button
            onClick={() => navigateTo('signin')}
            className="text-green-500 hover:text-green-400 font-semibold"
          >
            Sign Up
          </button>
        </p>
      </div>
    </div>
  );
}

export default LogIn;