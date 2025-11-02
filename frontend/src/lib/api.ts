import axios from 'axios'
import type { TokenResponse, RunCodeResponse } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function getToken(participantName: string = 'user'): Promise<TokenResponse> {
  const response = await api.post<TokenResponse>('/token', {
    participant_name: participantName,
  })
  return response.data
}

export async function runCode(
  code: string,
  problemId: string,
  testCases: string
): Promise<RunCodeResponse> {
  const response = await api.post<RunCodeResponse>('/run-code', {
    code,
    problem_id: problemId,
    test_cases: testCases,
  })
  return response.data
}


