import { useState } from "react"
import { CodeEditor } from "@/components/CodeEditor"
import { VoiceAgent } from "@/components/VoiceAgent"
import { Transcript } from "@/components/Transcript"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { runCode } from "@/lib/api"
import type { Problem, TranscriptMessage, RunCodeResponse } from "@/types"

function App() {
  const [selectedProblem, setSelectedProblem] = useState<Problem | null>(null)
  const [code, setCode] = useState(`# Start coding once the agent selects a problem
# The agent will ask you what topic you want to practice
`)
  const [transcript, setTranscript] = useState<TranscriptMessage[]>([])
  const [testResults, setTestResults] = useState<RunCodeResponse | null>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [cursorPosition, setCursorPosition] = useState<{ line: number; column: number }>({ line: 0, column: 0 })

  const handleTranscriptUpdate = (role: "user" | "agent", content: string) => {
    setTranscript(prev => [
      ...prev,
      { role, content, timestamp: new Date() }
    ])
  }

  const handleProblemSelected = (problem: Problem) => {
    setSelectedProblem(problem)
    setTestResults(null)
    if (problem.codeTemplate) {
      setCode(problem.codeTemplate)
    } else {
      setCode(`def solution():
    # Write your code here
    pass
`)
    }
  }

  const handleRunTests = async () => {
    if (!selectedProblem || !selectedProblem.testCases) {
      alert("No test cases available for this problem")
      return
    }

    setIsRunning(true)
    setTestResults(null)

    try {
      const results = await runCode(code, selectedProblem.id, selectedProblem.testCases)
      setTestResults(results)
    } catch (error) {
      console.error("Error running tests:", error)
      setTestResults({
        success: false,
        error: "Failed to run tests. Please try again."
      })
    } finally {
      setIsRunning(false)
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toUpperCase()) {
      case "EASY": return "text-emerald-600 bg-emerald-50"
      case "MEDIUM": return "text-amber-600 bg-amber-50"
      case "HARD": return "text-rose-600 bg-rose-50"
      default: return "text-slate-600 bg-slate-50"
    }
  }

  return (
    <div className="h-screen flex flex-col bg-white">
      {/* Header - LeetCode Style */}
      <header className="border-b border-gray-200 bg-white">
        <div className="px-5 py-2.5 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <img 
              src="/logocodecoach.png" 
              alt="CodeCoach" 
              className="h-8 w-auto"
            />
            {selectedProblem && (
              <div className="flex items-center gap-3">
                <span className="text-base font-medium text-gray-800">{selectedProblem.title}</span>
                <Badge className={`${getDifficultyColor(selectedProblem.difficulty)} px-2.5 py-0.5 text-xs font-medium rounded-full`}>
                  {selectedProblem.difficulty}
                </Badge>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content - LeetCode Split Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Problem Description */}
        <div className="w-1/2 flex flex-col border-r border-gray-200 bg-white">
          {/* Tab Header */}
          <div className="flex border-b border-gray-200 bg-white">
            <div className="px-4 py-3 text-sm font-medium text-gray-900 relative">
              Description
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gray-900" />
            </div>
          </div>

          {/* Content Area */}
          <div className="flex-1 overflow-y-auto">
            {selectedProblem ? (
              <div className="p-4 px-5">
                <div className="space-y-4">
                  <div className="text-sm leading-7 text-gray-700">
                    {selectedProblem.description.split('\n\n').map((paragraph, idx) => (
                      <div key={idx} className="mb-4">
                        {paragraph.split('\n').map((line, lineIdx) => (
                          <div key={lineIdx}>
                            {line.startsWith('Example') ? (
                              <p className="font-medium text-gray-900 mt-6 mb-2">{line}</p>
                            ) : line.startsWith('Input:') || line.startsWith('Output:') || line.startsWith('Explanation:') ? (
                              <pre className="text-sm font-mono bg-gray-50 px-3 py-2 rounded my-1">{line}</pre>
                            ) : line.startsWith('Constraints:') ? (
                              <p className="font-medium text-gray-900 mt-6 mb-2">{line}</p>
                            ) : line.startsWith('-') ? (
                              <p className="ml-4 my-1">{line}</p>
                            ) : (
                              <p>{line}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full p-8">
                <div className="text-center max-w-md">
                  <h3 className="text-xl font-semibold text-gray-800 mb-2">Ready to Practice</h3>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    Start a session with Alex. Ask what topic you want to practice, and he'll guide you through selecting the right problems.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Panel - Code Editor (50%) + Voice/Transcript (50%) */}
        <div className="w-1/2 flex flex-col bg-white">
          {/* Code Editor Section - 50% */}
          <div className="h-1/2 flex flex-col border-b border-gray-200">
            {/* Editor Header */}
            <div className="flex items-center justify-between border-b border-gray-200 bg-white px-4 py-2">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-900">Code</span>
              </div>
              {selectedProblem && (
                <Button
                  onClick={handleRunTests}
                  disabled={isRunning}
                  className="bg-white hover:bg-gray-50 text-gray-900 border border-gray-300 text-sm px-4 py-1.5 h-8 rounded shadow-sm font-medium"
                >
                  {isRunning ? "Running..." : "▶ Run"}
                </Button>
              )}
            </div>

            {/* Code Editor */}
            <div className="flex-1 overflow-hidden">
              <CodeEditor
                code={code}
                onChange={(value) => setCode(value || "")}
                onCursorPositionChange={(line, column) => setCursorPosition({ line, column })}
                language="python"
              />
            </div>

            {/* Test Results Panel */}
            {testResults && (
              <div className="border-t border-gray-200 bg-white max-h-48 overflow-y-auto">
                <div className="px-4 py-2 bg-gray-50 border-b border-gray-200">
                  <span className="text-sm font-medium text-gray-900">Testcase</span>
                </div>
                <div className="p-4">
                  {testResults.success ? (
                    <div className="space-y-3">
                      <div className={`flex items-center gap-2 text-sm font-medium ${testResults.all_passed ? 'text-emerald-600' : 'text-rose-600'}`}>
                        {testResults.all_passed ? (
                          <><span className="text-lg">✓</span> Accepted</>
                        ) : (
                          <><span className="text-lg">✗</span> Wrong Answer</>
                        )}
                      </div>
                      <div className="space-y-2">
                        {testResults.results?.map((result) => (
                          <div key={result.test_case} className={`p-3 rounded border text-sm ${result.passed ? 'bg-emerald-50 border-emerald-200' : 'bg-rose-50 border-rose-200'}`}>
                            <div className={`font-medium mb-1 ${result.passed ? 'text-emerald-700' : 'text-rose-700'}`}>
                              Test Case {result.test_case}
                            </div>
                            <div className="text-xs text-gray-600 space-y-1 font-mono">
                              <div><span className="text-gray-500">Input:</span> {result.input}</div>
                              {result.passed ? (
                                <div><span className="text-gray-500">Output:</span> {result.output}</div>
                              ) : (
                                <div className="text-rose-600"><span className="text-gray-500">Error:</span> {result.error}</div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="text-rose-600 text-sm">
                      <div className="font-medium mb-1">Error</div>
                      <div className="text-xs font-mono">{testResults.error}</div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Voice Coach & Transcript Section - 50% */}
          <div className="h-1/2 flex flex-col bg-white">
            {/* Voice Coach */}
            <div className="border-b border-gray-200 p-4">
              <VoiceAgent
                problem={selectedProblem}
                currentCode={code}
                cursorPosition={cursorPosition}
                onTranscriptUpdate={handleTranscriptUpdate}
                onProblemSelected={handleProblemSelected}
              />
            </div>

            {/* Transcript */}
            <div className="flex-1 overflow-hidden">
              <Transcript messages={transcript} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
