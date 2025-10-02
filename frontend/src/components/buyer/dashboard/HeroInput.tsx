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
      <div className="absolute -inset-1 rounded-lg bg-gradient-to-r from-[var(--color-ai-primary)] to-[var(--color-brand-primary)] opacity-20 blur-xl" />
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-center gap-3 rounded-lg border border-gray-200 bg-white p-2 shadow-lg transition-all focus-within:border-[var(--color-ai-primary)] focus-within:ring-2 focus-within:ring-[var(--color-ai-primary)]/20">
          <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-md bg-gradient-to-br from-[var(--color-ai-primary)] to-[var(--color-brand-primary)] text-white">
            <Sparkles className="h-5 w-5" />
          </div>
          <input
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="Need 200 design seats · budget $1,000/seat/year · SOC 2 required"
            className="flex-1 bg-transparent py-2 text-base text-[var(--core-color-text-primary)] placeholder:text-[var(--core-color-text-muted)] focus:outline-none"
          />
          <button
            type="submit"
            disabled={!value.trim()}
            className="flex h-10 items-center gap-2 rounded-md border border-[var(--accent-mint)] bg-white px-4 text-sm font-semibold text-[var(--core-color-text-primary)] transition-all hover:bg-[var(--accent-mint)]/30 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Start
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </form>
    </div>
  )
}
