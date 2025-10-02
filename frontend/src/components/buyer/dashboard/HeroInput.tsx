import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, ArrowRight } from 'lucide-react'

interface HeroInputProps {
  onSubmit?: (description: string) => void
}

export function HeroInput({ onSubmit }: HeroInputProps) {
  const navigate = useNavigate()
  const [value, setValue] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (value.trim()) {
      if (onSubmit) {
        onSubmit(value)
      } else {
        // Navigate to new request with pre-filled description
        navigate('/requests/new', { state: { description: value } })
      }
    }
  }

  return (
    <div className="relative">
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-center gap-3 rounded-lg border border-gray-200 bg-white p-2 shadow-sm transition-all focus-within:border-[var(--agent-accent)] focus-within:ring-2 focus-within:ring-[var(--agent-accent)]/30">
          <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-md border border-[var(--agent-accent)] bg-white text-[var(--core-color-text-primary)]">
            <Sparkles className="h-5 w-5" />
          </div>
          <input
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="Need 200 design seats · Budget $1,000/seat/year · SOC2 required"
            className="flex-1 bg-transparent py-2 text-base text-[var(--core-color-text-primary)] placeholder:text-[var(--core-color-text-muted)] focus:outline-none"
          />
          <button
            type="submit"
            disabled={!value.trim()}
            className="flex h-11 items-center gap-2 rounded-md bg-[var(--agent-accent)] px-5 text-sm font-semibold text-white transition-all hover:opacity-95 disabled:opacity-40 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--agent-accent)]/60"
          >
            Describe
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </form>
    </div>
  )
}
