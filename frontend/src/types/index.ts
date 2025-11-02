export interface Problem {
  id: string
  title: string
  difficulty: "Easy" | "Medium" | "Hard" | "EASY" | "MEDIUM" | "HARD"
  description: string
  codeTemplate?: string
  topics?: string[]
  testCases?: string
}

export interface TokenResponse {
  token: string
  room_name: string
  url: string
}

export interface TranscriptMessage {
  role: "user" | "agent"
  content: string
  timestamp: Date
}

export interface TestResult {
  test_case: number
  input: string
  output: string | null
  passed: boolean
  error: string | null
}

export interface RunCodeResponse {
  success: boolean
  all_passed?: boolean
  results?: TestResult[]
  error?: string
  traceback?: string
}

