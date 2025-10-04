import { useEffect, useRef, useState } from 'react'

interface BreathingNumberProps {
  base: number
  amplitude?: number // how much to increase above base
  periodMs?: number // full up-and-down cycle duration
  format?: (n: number) => string
}

// Subtle, perpetual oscillation between base and base + amplitude using a sine wave
export function BreathingNumber({ base, amplitude = 2, periodMs = 2400, format }: BreathingNumberProps) {
  const [display, setDisplay] = useState<number>(base)
  const startRef = useRef<number | null>(null)
  const rafRef = useRef<number | null>(null)

  useEffect(() => {
    const step = (t: number) => {
      if (startRef.current == null) startRef.current = t
      const elapsed = t - startRef.current
      const phase = (elapsed % periodMs) / periodMs // 0..1
      const wave = Math.sin(phase * Math.PI * 2) // -1..1
      const normalized = (wave + 1) / 2 // 0..1
      const val = base + amplitude * normalized
      // Round gently to avoid flicker; keep integer feel
      setDisplay(Math.round(val))
      rafRef.current = requestAnimationFrame(step)
    }

    rafRef.current = requestAnimationFrame(step)
    return () => {
      if (rafRef.current != null) cancelAnimationFrame(rafRef.current)
      startRef.current = null
    }
  }, [base, amplitude, periodMs])

  const text = format ? format(display) : String(display)

  // Avoid SR noise: expose the stable base value to screen readers, hide animation
  return (
    <span aria-hidden="true">{text}</span>
  )
}
