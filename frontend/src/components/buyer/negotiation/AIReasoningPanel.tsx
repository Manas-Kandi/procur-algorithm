import { Box, Text, VStack, HStack, Badge } from '@chakra-ui/react'
import { Brain, Target, TrendingUp, Shield } from 'lucide-react'

interface AIReasoningPanelProps {
  reasoning: {
    summary: string
    factors: Array<{
      category: 'budget' | 'features' | 'compliance' | 'risk'
      weight: number
      description: string
      score: number
    }>
    recommendation: string
  }
}

const FACTOR_CONFIG = {
  budget: {
    icon: TrendingUp,
    label: 'Budget Fit',
    color: 'var(--core-color-success)',
  },
  features: {
    icon: Target,
    label: 'Feature Coverage',
    color: 'var(--core-color-brand-primary)',
  },
  compliance: {
    icon: Shield,
    label: 'Compliance',
    color: 'var(--core-color-purple-600)',
  },
  risk: {
    icon: Shield,
    label: 'Risk Assessment',
    color: 'var(--core-color-warning)',
  },
}

export function AIReasoningPanel({ reasoning }: AIReasoningPanelProps): JSX.Element {
  return (
    <Box
      borderWidth="1px"
      borderColor="var(--core-color-ai-border)"
      borderRadius="lg"
      bg="var(--core-color-ai-bg)"
      p={5}
    >
      <VStack align="stretch" gap={4}>
        {/* Header */}
        <HStack gap={2}>
          <Brain className="h-5 w-5" style={{ color: 'var(--core-color-ai-primary)' }} />
          <Text fontSize="md" fontWeight="semibold" color="var(--core-color-ai-primary)">
            AI Reasoning
          </Text>
        </HStack>

        {/* Summary */}
        <Text fontSize="sm" color="var(--core-color-text-primary)">
          {reasoning.summary}
        </Text>

        {/* Factors */}
        <VStack align="stretch" gap={3}>
          {reasoning.factors.map((factor, index) => {
            const config = FACTOR_CONFIG[factor.category]
            const Icon = config.icon
            const scorePercent = factor.score * 100

            return (
              <Box
                key={index}
                p={3}
                borderRadius="md"
                bg="var(--core-color-surface-canvas)"
                borderWidth="1px"
                borderColor="var(--core-color-border-subtle)"
              >
                <HStack justify="space-between" mb={2}>
                  <HStack gap={2}>
                    <Icon className="h-4 w-4" style={{ color: config.color }} />
                    <Text fontSize="sm" fontWeight="medium" color="var(--core-color-text-primary)">
                      {config.label}
                    </Text>
                    <Badge
                      fontSize="xs"
                      px={2}
                      py={0.5}
                      borderRadius="sm"
                      bg="var(--core-color-background-tertiary)"
                      color="var(--core-color-text-secondary)"
                    >
                      {(factor.weight * 100).toFixed(0)}% weight
                    </Badge>
                  </HStack>
                  <Badge
                    fontSize="xs"
                    px={2}
                    py={0.5}
                    borderRadius="sm"
                    bg={
                      scorePercent >= 80
                        ? 'var(--core-color-success-bg)'
                        : scorePercent >= 60
                        ? 'var(--core-color-warning-bg)'
                        : 'var(--core-color-danger-bg)'
                    }
                    color={
                      scorePercent >= 80
                        ? 'var(--core-color-success)'
                        : scorePercent >= 60
                        ? 'var(--core-color-warning)'
                        : 'var(--core-color-danger)'
                    }
                  >
                    {scorePercent.toFixed(0)}%
                  </Badge>
                </HStack>
                <Text fontSize="sm" color="var(--core-color-text-muted)">
                  {factor.description}
                </Text>
              </Box>
            )
          })}
        </VStack>

        {/* Recommendation */}
        <Box
          p={3}
          borderRadius="md"
          bg="var(--core-color-surface-canvas)"
          borderWidth="1px"
          borderColor="var(--core-color-border-default)"
        >
          <Text fontSize="xs" fontWeight="semibold" color="var(--core-color-text-primary)" mb={1}>
            💡 Recommendation
          </Text>
          <Text fontSize="sm" color="var(--core-color-text-muted)">
            {reasoning.recommendation}
          </Text>
        </Box>
      </VStack>
    </Box>
  )
}
