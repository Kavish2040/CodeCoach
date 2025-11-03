import { useEffect, useRef } from "react"
import type { TranscriptMessage } from "@/types"

interface TranscriptProps {
  messages: TranscriptMessage[]
}

export function Transcript({ messages }: TranscriptProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  return (
    <div className="h-full flex flex-col bg-white">
      <div className="border-b border-gray-200 px-4 py-3">
        <h3 className="text-sm font-medium text-gray-900">Conversation</h3>
      </div>
      
      <div
        ref={scrollRef}
        className="flex-1 p-4 overflow-y-auto space-y-3"
      >
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 text-xs">
            Your conversation with Maya will appear here
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[85%] rounded-lg px-3 py-2 ${
                  message.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-900"
                }`}
              >
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="text-xs font-medium opacity-90">
                    {message.role === "user" ? "You" : "Maya"}
                  </span>
                  <span className="text-xs opacity-60">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
                <p className="text-xs leading-relaxed whitespace-pre-wrap">{message.content}</p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
