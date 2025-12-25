import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

function Dashboard({ onLogout, onProblemSelect, userData }) {
  const [dashboardData, setDashboardData] = useState({
    problems: [],
    aiProblem: null,
    loading: true,
    progress: 0,
    problemsSolved: 0,
    totalProblems: 0,
    loadingAIProblem: true
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token');
        // Fetch all problems
        const problemsResponse = await fetch('http://localhost:8001/api/problems/', {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        if (!problemsResponse.ok) {
          throw new Error('Failed to fetch problems');
        }
        const problems = await problemsResponse.json();
        // Fetch user submissions to calculate progress
        let problemsSolved = 0;
        let solvedProblemIds = new Set();
        if (token) {
          try {
            const submissionsResponse = await fetch('http://localhost:8001/api/submissions/me', {
              headers: { 'Authorization': `Bearer ${token}` }
            });
            if (submissionsResponse.ok) {
              const submissions = await submissionsResponse.json();
              submissions.forEach(sub => {
                if (sub.all_tests_passed) {
                  solvedProblemIds.add(sub.problem_id);
                }
              });
              problemsSolved = solvedProblemIds.size;
            }
          } catch (err) {
            console.error('Error fetching submissions:', err);
          }
        }
        const totalProblems = problems.length;
        const progress = totalProblems > 0 ? Math.round((problemsSolved / totalProblems) * 100) : 0;
        setDashboardData(prev => ({
          ...prev,
          problems,
          totalProblems,
          problemsSolved,
          progress,
          loading: false
        }));
        // Fetch latest AI-generated problem
        if (token) {
          try {
            const aiProblemResponse = await fetch('http://localhost:8001/api/recommendations/ai-problem', {
              method: 'POST',
              headers: { 'Authorization': `Bearer ${token}` }
            });
            if (aiProblemResponse.ok) {
              const aiProblem = await aiProblemResponse.json();
              setDashboardData(prev => ({
                ...prev,
                aiProblem,
                loadingAIProblem: false
              }));
            } else {
              setDashboardData(prev => ({
                ...prev,
                loadingAIProblem: false
              }));
            }
          } catch (err) {
            console.error('Error fetching AI problem:', err);
            setDashboardData(prev => ({
              ...prev,
              loadingAIProblem: false
            }));
          }
        } else {
          setDashboardData(prev => ({
            ...prev,
            loadingAIProblem: false
          }));
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        setDashboardData(prev => ({
          ...prev,
          loading: false,
          loadingAIProblem: false
        }));
      }
    };
    fetchData();
  }, [userData]);

  const getDifficultyColor = (difficulty) => {
    switch(difficulty?.toLowerCase()) {
      case 'easy': return 'text-green-400 bg-green-500/10 border-green-500/30';
      case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30';
      case 'hard': return 'text-red-400 bg-red-500/10 border-red-500/30';
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500/30';
    }
  };

  return (
    <div className="min-h-screen bg-black p-6">
      <div className="max-w-7xl mx-auto">
        {/* Progress Section */}
        <div className="mb-8 bg-zinc-900 border border-green-500/30 rounded-lg p-6 shadow-xl shadow-green-500/10">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-green-500">Your Progress</h2>
            <span className="text-gray-400 text-sm">
              {dashboardData.problemsSolved} / {dashboardData.totalProblems} problems solved
            </span>
          </div>
          <div className="relative w-full h-8 bg-zinc-800 rounded-lg overflow-hidden border border-green-500/20">
            <div
              className="absolute top-0 left-0 h-full bg-gradient-to-r from-green-600 to-green-400 transition-all duration-500 ease-out flex items-center justify-center"
              style={{ width: `${dashboardData.progress}%` }}
            >
              {dashboardData.progress > 0 && (
                <span className="text-black font-bold text-sm">{dashboardData.progress}%</span>
              )}
            </div>
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Problems Section */}
          <div className="bg-zinc-900 border border-green-500/30 rounded-lg p-6 shadow-xl shadow-green-500/10">
            <div className="flex items-center mb-6">
              <svg className="w-8 h-8 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <h2 className="text-2xl font-bold text-green-500">Problems</h2>
            </div>
            {dashboardData.loading ? (
              <div className="text-center py-12">
                <div className="w-12 h-12 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <div className="text-green-500 text-lg">Loading problems...</div>
              </div>
            ) : dashboardData.problems.length === 0 ? (
              <div className="text-center py-12">
                <svg className="w-16 h-16 mx-auto text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="text-gray-400 mb-2">No problems available</p>
                <p className="text-gray-500 text-sm">Check if backend is running</p>
              </div>
            ) : (
              <div className="space-y-3">
                {dashboardData.problems.map((problem) => (
                  <button
                    key={problem.id}
                    onClick={() => onProblemSelect(problem)}
                    className="w-full text-left border rounded-lg p-4 bg-zinc-800 border-green-500/20 hover:border-green-500/50 hover:bg-zinc-800/80 transition duration-200"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-bold text-lg text-green-400">{problem.title}</h3>
                      <span className={`text-xs px-2 py-1 rounded border font-semibold ${getDifficultyColor(problem.difficulty)}`}>
                        {problem.difficulty}
                      </span>
                    </div>
                    <p className="text-gray-400 text-sm line-clamp-2">{problem.description}</p>
                    {problem.tags && problem.tags.length > 0 && (
                      <div className="mt-2 flex gap-2 flex-wrap">
                        {problem.tags.slice(0, 3).map((tag, idx) => (
                          <span key={idx} className="text-green-500 text-xs font-semibold bg-green-500/10 px-2 py-1 rounded">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
          {/* AI Recommendations Section */}
          <div className="bg-zinc-900 border border-blue-500/30 rounded-lg p-6 shadow-xl shadow-blue-500/10">
            <div className="flex items-center mb-6">
              <svg className="w-8 h-8 text-blue-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <h2 className="text-2xl font-bold text-blue-500">AI Recommendations</h2>
            </div>
            {dashboardData.loadingAIProblem ? (
              <div className="text-center py-12">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <div className="text-blue-500 text-lg">Loading AI problem...</div>
              </div>
            ) : !dashboardData.aiProblem ? (
              <div className="text-center py-12">
                <svg className="w-16 h-16 mx-auto text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <p className="text-gray-400 mb-2">No AI Problem Yet</p>
                <p className="text-gray-500 text-sm">Solve problems to get personalized AI-generated problems</p>
              </div>
            ) : (
              <button
                className="w-full text-left border rounded-lg p-4 bg-zinc-800 border-blue-500/20 hover:border-blue-500/50 hover:bg-zinc-800/80 transition duration-200"
                onClick={() => onProblemSelect(dashboardData.aiProblem)}
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold text-lg text-blue-400">{dashboardData.aiProblem.title}</h3>
                  <span className={`text-xs px-2 py-1 rounded border font-semibold ${getDifficultyColor(dashboardData.aiProblem.difficulty)}`}>
                    AI Generated
                  </span>
                </div>
                <div className="prose prose-invert max-w-none text-gray-400 text-sm mb-2">
                  <ReactMarkdown>{dashboardData.aiProblem.description}</ReactMarkdown>
                </div>
                {dashboardData.aiProblem.tags && dashboardData.aiProblem.tags.length > 0 && (
                  <div className="mt-2 flex gap-2 flex-wrap">
                    {dashboardData.aiProblem.tags.slice(0, 3).map((tag, idx) => (
                      <span key={idx} className="text-blue-500 text-xs font-semibold bg-blue-500/10 px-2 py-1 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;