import { useState } from 'react';
import SignIn from './pages/SignIn';
import LogIn from './pages/LogIn';
import Dashboard from './pages/Dashboard';
import Exercise from './pages/Exercise';
import Feedback from './pages/Feedback';
import Navbar from './components/Navbar';

function App() {
  const [currentPage, setCurrentPage] = useState('signin');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userData, setUserData] = useState(null);
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [submittedCode, setSubmittedCode] = useState(null);

  const handleLogin = (user) => {
    setIsLoggedIn(true);
    setUserData(user);
    setCurrentPage('dashboard');
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUserData(null);
    setCurrentPage('login');
    setSelectedProblem(null);
    setSubmittedCode(null);
  };

  const navigateTo = (page) => {
    setCurrentPage(page);
  };

  const handleProblemSelect = (problem) => {
    setSelectedProblem(problem);
    setCurrentPage('exercise');
  };

  const handleCodeSubmit = (code) => {
    setSubmittedCode(code);
    setCurrentPage('feedback');
  };

  return (
    <div>
      {isLoggedIn && (
        <Navbar 
          currentPage={currentPage} 
          navigateTo={navigateTo} 
          onLogout={handleLogout}
          userData={userData}
        />
      )}
      
      {currentPage === 'signin' && (
        <SignIn navigateTo={navigateTo} />
      )}
      
      {currentPage === 'login' && (
        <LogIn navigateTo={navigateTo} onLogin={handleLogin} />
      )}
      
      {currentPage === 'dashboard' && (
        <Dashboard 
          onLogout={handleLogout} 
          onProblemSelect={handleProblemSelect}
          userData={userData}
        />
      )}
      
      {currentPage === 'exercise' && (
        <Exercise 
          onLogout={handleLogout}
          problem={selectedProblem}
          onCodeSubmit={handleCodeSubmit}
          navigateTo={navigateTo}
        />
      )}
      
      {currentPage === 'feedback' && (
        <Feedback 
          onLogout={handleLogout}
          submittedCode={submittedCode}
          problem={selectedProblem}
          navigateTo={navigateTo}
        />
      )}
    </div>
  );
}

export default App;
