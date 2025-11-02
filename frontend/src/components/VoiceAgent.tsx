import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Room, RoomEvent, Track } from "livekit-client"
import { getToken } from "@/lib/api"
import type { Problem } from "@/types"

interface VoiceAgentProps {
  problem: Problem | null
  currentCode: string
  cursorPosition: { line: number; column: number }
  onTranscriptUpdate: (role: "user" | "agent", content: string) => void
  onProblemSelected: (problem: Problem) => void
}

export function VoiceAgent({ problem, currentCode, cursorPosition, onTranscriptUpdate, onProblemSelected }: VoiceAgentProps) {
  const [isConnected, setIsConnected] = useState(false)
  
  const [isConnecting, setIsConnecting] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [room, setRoom] = useState<Room | null>(null)
  const audioRef = useRef<HTMLAudioElement>(null)

  const startCall = async () => {
    setIsConnecting(true)
    try {
      const { token, url } = await getToken()
      const newRoom = new Room()

      newRoom.on(RoomEvent.Connected, () => {
        console.log("Connected to room")
        setIsConnected(true)
        setIsConnecting(false)
        // Send initial code update if problem exists
        if (problem) {
          sendCodeUpdate(newRoom)
        }
      })

      newRoom.on(RoomEvent.Disconnected, () => {
        console.log("Disconnected from room")
        setIsConnected(false)
        setRoom(null)
      })

      // Listen for data messages from the agent
      newRoom.on(RoomEvent.DataReceived, (payload, _participant, _kind, _topic) => {
        try {
          const decoder = new TextDecoder()
          const message = JSON.parse(decoder.decode(payload))
          
          console.log("=== DATA RECEIVED FROM AGENT ===", message)
          
          if (message.type === "problem_selected" && message.problem) {
            console.log("=== LOADING PROBLEM ON SCREEN ===", message.problem.title)
            onProblemSelected(message.problem)
          }
        } catch (error) {
          console.error("=== ERROR PROCESSING DATA MESSAGE ===", error)
        }
      })

      newRoom.on(RoomEvent.TranscriptionReceived, (segments, participant) => {
        // Only process final transcriptions to avoid showing incremental updates
        const finalSegments = segments.filter(s => s.final)
        if (finalSegments.length === 0) return
        
        const text = finalSegments.map(s => s.text).join(' ')
        const role = participant?.identity.includes('agent') ? 'agent' : 'user'
        if (text.trim()) {
          onTranscriptUpdate(role, text)
        }
      })

      // Handle audio tracks from the agent
      newRoom.on(RoomEvent.TrackSubscribed, (track, _publication, participant) => {
        console.log('Track subscribed:', track.kind, 'from', participant.identity)
        
        if (track.kind === Track.Kind.Audio && audioRef.current) {
          const audioElement = track.attach()
          audioElement.autoplay = true
          audioElement.volume = 1.0
          
          // Replace the audio element's source
          if (audioRef.current.parentElement) {
            audioRef.current.parentElement.replaceChild(audioElement, audioRef.current)
            audioRef.current = audioElement as HTMLAudioElement
          }
          
          console.log('Audio track attached and playing')
        }
      })

      await newRoom.connect(url, token)
      
      // Enable microphone so the agent can hear you
      await newRoom.localParticipant.setMicrophoneEnabled(true)
      console.log("Microphone enabled")
      
      setRoom(newRoom)

    } catch (error) {
      console.error("Failed to connect:", error)
      alert("Failed to connect to voice agent. Please try again.")
      setIsConnecting(false)
    }
  }

  const endCall = async () => {
    if (room) {
      await room.disconnect()
      setRoom(null)
      setIsConnected(false)
      setIsMuted(false)
    }
  }

  const toggleMute = () => {
    if (room) {
      room.localParticipant.setMicrophoneEnabled(isMuted)
      setIsMuted(!isMuted)
    }
  }

  const sendCodeUpdate = (targetRoom: Room = room!) => {
    if (!targetRoom) {
      console.log("=== CANNOT SEND CODE UPDATE: No room ===")
      return
    }

    const data = JSON.stringify({
      type: "code_update",
      code: currentCode,
      problem: problem?.description || "",
      cursor_line: cursorPosition.line,
      cursor_column: cursorPosition.column,
    })

    console.log("=== SENDING CODE UPDATE ===")
    console.log("Room state:", targetRoom.state)
    console.log("Code length:", currentCode.length)
    console.log("Problem length:", problem?.description?.length || 0)
    console.log("Cursor position:", `Line ${cursorPosition.line + 1}, Col ${cursorPosition.column + 1}`)
    console.log("Data to send:", data.substring(0, 200))

    const encoder = new TextEncoder()
    targetRoom.localParticipant.publishData(
      encoder.encode(data),
      { reliable: true }
    )
    
    console.log("=== CODE UPDATE SENT ===")
  }

  useEffect(() => {
    if (isConnected && room) {
      const timeoutId = setTimeout(() => {
        sendCodeUpdate()
      }, 1000)

      return () => clearTimeout(timeoutId)
    }
  }, [isConnected, room, currentCode, problem, cursorPosition])

  return (
    <div className="space-y-3">
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-1.5">AI Voice Coach</h3>
        <p className="text-xs text-gray-600 leading-relaxed flex items-center gap-2">
          {isConnected ? (
            <>
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              Alex is listening. Speak anytime you need help.
            </>
          ) : (
            "Connect with Alex for personalized guidance and problem selection."
          )}
        </p>
      </div>

      <div className="flex gap-2">
        {!isConnected ? (
          <Button
            onClick={startCall}
            disabled={isConnecting}
            className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium h-9 rounded transition-colors"
          >
            {isConnecting ? "Connecting..." : "Start Session"}
          </Button>
        ) : (
          <>
            <Button
              onClick={toggleMute}
              variant="outline"
              className="flex-1 border-gray-300 hover:bg-gray-50 text-gray-700 text-sm font-medium h-9 rounded transition-colors flex items-center justify-center gap-1.5"
            >
              {isMuted ? (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" clipRule="evenodd" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
                  </svg>
                  Unmute
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                  </svg>
                  Mute
                </>
              )}
            </Button>
            <Button
              onClick={endCall}
              className="flex-1 bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium h-9 rounded transition-colors"
            >
              End
            </Button>
          </>
        )}
      </div>
      
      {/* Hidden audio element for agent voice */}
      <audio ref={audioRef} style={{ display: 'none' }} />
    </div>
  )
}
