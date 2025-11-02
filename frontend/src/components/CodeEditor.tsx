import Editor from "@monaco-editor/react"

interface CodeEditorProps {
  code: string
  onChange: (value: string | undefined) => void
  language?: string
}

export function CodeEditor({ code, onChange, language = "python" }: CodeEditorProps) {
  return (
    <Editor
      height="100%"
      defaultLanguage={language}
      value={code}
      onChange={onChange}
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
