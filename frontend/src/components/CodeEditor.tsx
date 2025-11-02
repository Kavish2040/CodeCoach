import Editor from "@monaco-editor/react"
import type { editor } from "monaco-editor"

interface CodeEditorProps {
  code: string
  onChange: (value: string | undefined) => void
  onCursorPositionChange?: (line: number, column: number) => void
  language?: string
}

export function CodeEditor({ code, onChange, onCursorPositionChange, language = "python" }: CodeEditorProps) {
  const handleEditorDidMount = (editor: editor.IStandaloneCodeEditor) => {
    // Track cursor position changes
    editor.onDidChangeCursorPosition((e) => {
      if (onCursorPositionChange) {
        // Monaco uses 1-based line numbers, but we'll send 0-based to backend
        onCursorPositionChange(e.position.lineNumber - 1, e.position.column - 1)
      }
    })
  }

  return (
    <Editor
      height="100%"
      defaultLanguage={language}
      value={code}
      onChange={onChange}
      onMount={handleEditorDidMount}
      theme="vs-light"
      options={{
        minimap: { enabled: false },
        fontSize: 14,
        lineNumbers: "on",
        roundedSelection: true,
        scrollBeyondLastLine: false,
        automaticLayout: true,
        tabSize: 4,
        fontFamily: "'JetBrains Mono', 'Fira Code', Consolas, monospace",
        padding: { top: 16, bottom: 16 },
        lineHeight: 24,
        scrollbar: {
          vertical: 'visible',
          horizontal: 'visible',
        },
      }}
    />
  )
}

