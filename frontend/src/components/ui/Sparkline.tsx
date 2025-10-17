import React from 'react'
import { Box } from '@chakra-ui/react'

export interface SparklineProps {
  data: number[]
  width?: number
  height?: number
  color?: string // chakra token e.g. 'blue.emphasized' or hex
  fillOpacity?: number
}

export function Sparkline({ data, width = 120, height = 36, color = 'blue.emphasized', fillOpacity = 0.08 }: SparklineProps) {
  const safe = Array.isArray(data) && data.length > 1 ? data : [0, 1]
  const min = Math.min(...safe)
  const max = Math.max(...safe)
  const span = max - min || 1

  const points = safe.map((v, i) => {
    const x = (i / (safe.length - 1)) * (width - 2) + 1
    const y = height - ((v - min) / span) * (height - 2) - 1
    return [x, y]
  })

  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'}${p[0]},${p[1]}`).join(' ')
  const areaD = `${pathD} L${width - 1},${height - 1} L1,${height - 1} Z`

  return (
    <Box as="svg" width={width} height={height} overflow="visible" color={color}>
      <path d={areaD} fill="currentColor" opacity={fillOpacity} />
      <path d={pathD} fill="none" stroke="currentColor" strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
    </Box>
  )
}

export default Sparkline
