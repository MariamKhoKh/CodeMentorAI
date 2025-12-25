import { useState, useEffect } from 'react';

function Feedback({ onLogout, submittedCode, problem, navigateTo }) {
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check if we have analysis data already
    if (submittedCode?.analysis) {
      setFeedback(submittedCode.analysis);
      setLoading(false);
    } else if (submittedCode?.submissionId) {
      // Fetch analysis from backend
      const fetchAnalysis = async () => {
        try {
          const token = localStorage.getItem('token');
          const response = await fetch(`http://localhost:8000/api/analysis/${submittedCode.submissionId}`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (!response.ok) {
            throw new Error('Failed to fetch AI feedback');
          }

          const data = await response.json();
          setFeedback(data);
          setLoading(false);
        } catch (err) {
          console.error('Error fetching feedback:', err);
          setError('Failed to load AI feedback. Make sure backend is running.');
          setLoading(false);
        }
      };

      fetchAnalysis();
    } else {
      setError('No submission found');
      setLoading(false);
    }
  }, [submittedCode]);

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <h2 className="text-2xl font-bold text-green-500 mb-2">AI is Analyzing Your Code...</h2>
          <p className="text-gray-400">Generating personalized feedback with GPT-5</p>
          <p className="text-gray-500 text-sm mt-2">This may take a few seconds</p>
        </div>
      </div>
    );
  }

  if (error || !feedback) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <svg className="w-20 h-20 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 className="text-2xl font-bold text-red-400 mb-4">{error || 'No Feedback Available'}</h2>
          <p className="text-gray-400 mb-6">Make sure backend is running and you submitted code</p>
          <button
            onClick={() => navigateTo('dashboard')}
            className="px-6 py-2 bg-green-600 text-black rounded-lg font-bold hover:bg-green-500 transition duration-200"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  // Calculate score based on complexity match
  const score = feedback.complexity_match ? Math.round(feedback.complexity_match * 100) : null;
  const testsPassed = submittedCode?.passedTests || 0;
  const totalTests = submittedCode?.totalTests || 0;

  return (
    <div className="min-h-screen bg-black p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-4xl font-bold text-green-500">AI-Generated Feedback</h1>
            <button
              onClick={() => navigateTo('dashboard')}
              className="px-6 py-2 bg-zinc-900 border border-green-500/30 text-green-500 rounded-lg hover:bg-zinc-800 transition duration-200"
            >
              Back to Dashboard
            </button>
          </div>
          {problem && (
            <p className="text-gray-400">Problem: <span className="text-green-400 font-semibold">{problem.title}</span></p>
          )}
        </div>

        {/* Test Results Summary */}
        <div className="mb-8 bg-zinc-900 border border-green-500/30 rounded-lg p-6 shadow-xl shadow-green-500/10">
          <h2 className="text-2xl font-bold text-green-500 mb-4">Test Results</h2>
          <div className="flex items-center justify-between mb-6">
            <div>
              <p className="text-gray-400">Tests Passed</p>
              <p className={`text-3xl font-bold ${submittedCode?.allTestsPassed ? 'text-green-400' : 'text-yellow-400'}`}>
                {testsPassed} / {totalTests}
              </p>
            </div>
            {submittedCode?.allTestsPassed && (
              <svg className="w-16 h-16 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
          </div>

          {/* Detailed Test Results - Show ALL test cases */}
          {submittedCode?.testResults && submittedCode.testResults.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-gray-300 mb-3">Test Case Details:</h3>
              {submittedCode.testResults.map((test, idx) => (
                <div 
                  key={idx}
                  className={`border rounded-lg p-4 ${
                    test.status === 'passed' 
                      ? 'border-green-500/30 bg-green-500/5' 
                      : 'border-red-500/30 bg-red-500/5'
                  }`}
                >
                  <div className="flex items-center mb-2">
                    {test.status === 'passed' ? (
                      <svg className="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    )}
                    <span className="font-semibold text-gray-300">
                      Test Case #{test.test_case_id + 1} - {test.status.toUpperCase()}
                      {test.is_hidden && <span className="ml-2 text-xs text-gray-500">(Hidden)</span>}
                    </span>
                  </div>
                  <div className="text-sm space-y-1 text-gray-400">
                    <div>
                      <span className="font-semibold">Input:</span> 
                      <code className="ml-2 text-green-300">{JSON.stringify(test.input)}</code>
                    </div>
                    <div>
                      <span className="font-semibold">Expected:</span> 
                      <code className="ml-2 text-green-300">{JSON.stringify(test.expected_output)}</code>
                    </div>
                    <div>
                      <span className="font-semibold">Your Output:</span> 
                      <code className={`ml-2 ${test.status === 'passed' ? 'text-green-300' : 'text-red-300'}`}>
                        {JSON.stringify(test.actual_output)}
                      </code>
                    </div>
                    {test.error_message && (
                      <div className="text-red-400 mt-2">
                        <span className="font-semibold">Error:</span> {test.error_message}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Complexity Analysis */}
        {score !== null && (
          <div className="mb-8 bg-zinc-900 border border-blue-500/30 rounded-lg p-6 shadow-xl shadow-blue-500/10">
            <h2 className="text-2xl font-bold text-blue-500 mb-4">Complexity Analysis</h2>
            <div className="grid grid-cols-2 gap-6">
              <div>
                <p className="text-gray-400 mb-2">Time Complexity</p>
                <p className="text-2xl font-bold text-green-400">{feedback.estimated_time_complexity}</p>
                <p className="text-sm text-gray-500">Optimal: {feedback.optimal_time_complexity}</p>
              </div>
              <div>
                <p className="text-gray-400 mb-2">Space Complexity</p>
                <p className="text-2xl font-bold text-green-400">{feedback.estimated_space_complexity}</p>
                <p className="text-sm text-gray-500">Optimal: {feedback.optimal_space_complexity}</p>
              </div>
            </div>
            <div className="mt-6">
              <p className="text-gray-400 mb-2">Optimization Score</p>
              <div className="flex items-center">
                <div className="flex-1 bg-zinc-800 rounded-full h-4 mr-4">
                  <div 
                    className="bg-green-500 h-4 rounded-full transition-all duration-500"
                    style={{ width: `${score}%` }}
                  ></div>
                </div>
                <span className="text-2xl font-bold text-green-400">{score}%</span>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Code Structure */}
          {feedback.ast_features && (
            <div className="bg-zinc-900 border border-yellow-500/30 rounded-lg p-6 shadow-xl shadow-yellow-500/10">
              <h2 className="text-2xl font-bold text-yellow-500 mb-4">Code Structure</h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Loops</span>
                  <span className="text-green-400 font-semibold">{feedback.ast_features.loops}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Nested Loops</span>
                  <span className="text-green-400 font-semibold">{feedback.ast_features.nested_loops ? 'Yes' : 'No'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Uses HashMap</span>
                  <span className="text-green-400 font-semibold">{feedback.ast_features.uses_hashmap ? 'Yes' : 'No'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Recursion</span>
                  <span className="text-green-400 font-semibold">{feedback.ast_features.recursion ? 'Yes' : 'No'}</span>
                </div>
                {feedback.ast_features.data_structures && feedback.ast_features.data_structures.length > 0 && (
                  <div>
                    <span className="text-gray-400">Data Structures:</span>
                    <div className="flex gap-2 mt-2 flex-wrap">
                      {feedback.ast_features.data_structures.map((ds, idx) => (
                        <span key={idx} className="bg-yellow-500/10 text-yellow-400 px-2 py-1 rounded text-sm">
                          {ds}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Improvement Suggestions */}
          {feedback.improvement_suggestions && feedback.improvement_suggestions.length > 0 && (
            <div className="bg-zinc-900 border border-purple-500/30 rounded-lg p-6 shadow-xl shadow-purple-500/10">
              <h2 className="text-2xl font-bold text-purple-500 mb-4">Suggestions</h2>
              <ul className="space-y-3">
                {feedback.improvement_suggestions.map((suggestion, index) => (
                  <li key={index} className="flex items-start">
                    <svg className="w-5 h-5 text-purple-400 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                    <span className="text-gray-300">{suggestion}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* AI Explanation */}
        {feedback.feedback_text && (
          <div className="bg-zinc-900 border border-green-500/30 rounded-lg p-6 shadow-xl shadow-green-500/10">
            <div className="flex items-center mb-4">
              <svg className="w-8 h-8 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <h2 className="text-2xl font-bold text-green-500">AI Feedback (GPT-5)</h2>
            </div>
            <div className="text-gray-300 leading-relaxed whitespace-pre-line">
              {feedback.feedback_text}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Feedback;