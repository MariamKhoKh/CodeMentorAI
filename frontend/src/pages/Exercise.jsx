import { useState, useEffect } from 'react';

function Exercise({ onLogout, problem, onCodeSubmit, navigateTo }) {
  const [userCode, setUserCode] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [testResults, setTestResults] = useState(null);

  useEffect(() => {
    if (problem) {
      // Set starter code from backend or create template
      const starterCode = problem.starter_code?.python || 
        `# ${problem.title}\n\ndef solution():\n    # Your code here\n    pass\n`;
      setUserCode(starterCode);
      setTestResults(null);
    }
  }, [problem]);

  const handleSubmitCode = async () => {
    setIsSubmitting(true);
    setTestResults(null);
    
    try {
      const token = localStorage.getItem('token');
      
      // Step 1: Submit code
      const response = await fetch('http://localhost:8001/api/submissions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          problem_id: problem.id,
          code: userCode,
          language: 'python'
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit code');
      }
      
      const submissionData = await response.json();
      console.log('Submission created:', submissionData);
      
      // Show test results immediately
      setTestResults({
        passed: submissionData.passed_tests,
        total: submissionData.total_tests,
        all_passed: submissionData.all_tests_passed,
        results: (submissionData.test_results || []).map((tr) => ({
          passed: tr.status === 'passed',
          input: JSON.stringify(tr.input),
          output: JSON.stringify(tr.actual_output),
          expected: JSON.stringify(tr.expected_output),
          error: tr.error_message
        }))
      });
      
      // Step 2: Fetch analysis (AI feedback)
      const analysisRes = await fetch(`http://localhost:8001/api/analysis/${submissionData.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      let analysisData = null;
      if (analysisRes.ok) {
        analysisData = await analysisRes.json();
        console.log('Analysis received:', analysisData);
      }
      
      // Navigate to feedback page with all data
      onCodeSubmit({
        submissionId: submissionData.id,
        code: userCode,
        problemId: problem.id,
        testResults: submissionData.test_results,
        allTestsPassed: submissionData.all_tests_passed,
        passedTests: submissionData.passed_tests,
        totalTests: submissionData.total_tests,
        analysis: analysisData
      });
      
    } catch (error) {
      console.error('Error submitting code:', error);
      alert(`Failed to submit code: ${error.message}\n\nMake sure:\n1. Backend is running on port 8001\n2. You are logged in\n3. Problem is selected`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch(difficulty?.toLowerCase()) {
      case 'easy': return 'text-green-400 bg-green-500/10 border-green-500/30';
      case 'medium': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30';
      case 'hard': return 'text-red-400 bg-red-500/10 border-red-500/30';
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500/30';
    }
  };

  if (!problem) {
    return (
      <div className="h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <svg className="w-20 h-20 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h2 className="text-2xl font-bold text-gray-400 mb-4">No Problem Selected</h2>
          <p className="text-gray-500 mb-6">Select a problem from the dashboard to start coding</p>
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

  return (
    <div className="h-screen bg-black flex flex-col">
      <div className="flex-1 flex overflow-hidden">
        {/* Left Side - Problem Description */}
        <div className="w-1/2 border-r border-green-500/30 overflow-y-auto p-6">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-3xl font-bold text-green-500">{problem.title}</h2>
              {problem.difficulty && (
                <span className={`px-3 py-1 rounded-lg text-sm font-semibold border ${getDifficultyColor(problem.difficulty)}`}>
                  {problem.difficulty}
                </span>
              )}
            </div>
            {problem.tags && problem.tags.length > 0 && (
              <div className="mb-4 flex gap-2">
                {problem.tags.map((tag, idx) => (
                  <span key={idx} className="text-green-400 font-semibold text-sm bg-green-500/10 px-2 py-1 rounded">
                    {tag}
                  </span>
                ))}
              </div>
            )}
            <div className="text-gray-300 leading-relaxed whitespace-pre-line">
              {problem.description}
            </div>
          </div>

          {/* Test Results */}
          {testResults && (
            <div className="mt-6">
              <h3 className="text-xl font-bold text-green-400 mb-3">Test Results</h3>
              <div className="mb-4">
                <span className="text-gray-300">Passed: </span>
                <span className={testResults.all_passed ? 'text-green-400 font-bold' : 'text-yellow-400 font-bold'}>
                  {testResults.passed} / {testResults.total}
                </span>
              </div>
              <div className="space-y-2">
                {testResults.results.map((result, index) => (
                  <div 
                    key={index}
                    className={`border rounded-lg p-3 ${result.passed ? 'border-green-500/30 bg-green-500/5' : 'border-red-500/30 bg-red-500/5'}`}
                  >
                    <div className="flex items-center mb-2">
                      {result.passed ? (
                        <svg className="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      )}
                      <span className="text-sm font-semibold text-gray-300">Test Case {index + 1}</span>
                    </div>
                    <div className="text-sm text-gray-400 space-y-1">
                      <div><span className="font-semibold">Input:</span> {result.input}</div>
                      <div><span className="font-semibold">Your Output:</span> {result.output}</div>
                      <div><span className="font-semibold">Expected:</span> {result.expected}</div>
                      {result.error && (
                        <div className="text-red-400"><span className="font-semibold">Error:</span> {result.error}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Side - Code Editor */}
        <div className="w-1/2 flex flex-col">
          <div className="bg-zinc-900 border-b border-green-500/30 px-6 py-3 flex justify-between items-center">
            <h3 className="text-lg font-bold text-green-500">Code Editor</h3>
            <button
              onClick={handleSubmitCode}
              disabled={isSubmitting}
              className={`px-6 py-2 rounded-lg transition duration-200 text-sm font-semibold shadow-lg ${
                isSubmitting
                  ? 'bg-gray-600 text-gray-300 cursor-not-allowed'
                  : 'bg-green-600 text-black hover:bg-green-500 shadow-green-500/30'
              }`}
            >
              {isSubmitting ? 'Submitting & Getting AI Feedback...' : 'Submit for AI Feedback'}
            </button>
          </div>
          
          <textarea
            value={userCode}
            onChange={(e) => setUserCode(e.target.value)}
            className="flex-1 p-6 bg-black text-green-100 font-mono text-sm focus:outline-none resize-none"
            spellCheck="false"
            placeholder="# Write your code here..."
            style={{ 
              fontFamily: "'Fira Code', 'Courier New', monospace",
              tabSize: 4
            }}
          />
        </div>
      </div>
    </div>
  );
}

export default Exercise;