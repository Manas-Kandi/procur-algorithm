import { Box, Text, VStack, HStack, Button, Input, Textarea, useDisclosure } from '@chakra-ui/react'
import { DollarSign, Plus, Pause, CheckCircle, Settings } from 'lucide-react'
import { useState } from 'react'

interface EnhancedInterventionPanelProps {
  currentBudget?: { min?: number; max?: number }
  onAdjustBudget: (newBudget: { min?: number; max?: number }) => void
  onAddRequirement: (requirement: string) => void
  onPauseNegotiations: () => void
  onAcceptOffer: (sessionId: string) => void
  canAccept?: boolean
  bestSessionId?: string
}

export function EnhancedInterventionPanel({
  currentBudget,
  onAdjustBudget,
  onAddRequirement,
  onPauseNegotiations,
  onAcceptOffer,
  canAccept = false,
  bestSessionId,
}: EnhancedInterventionPanelProps): JSX.Element {
  const { open: isBudgetOpen, onToggle: toggleBudget } = useDisclosure()
  const { open: isRequirementOpen, onToggle: toggleRequirement } = useDisclosure()

  const [budgetMax, setBudgetMax] = useState(currentBudget?.max?.toString() || '')
  const [budgetMin, setBudgetMin] = useState(currentBudget?.min?.toString() || '')
  const [newRequirement, setNewRequirement] = useState('')

  const handleBudgetSave = () => {
    onAdjustBudget({
      min: budgetMin ? parseFloat(budgetMin) : undefined,
      max: budgetMax ? parseFloat(budgetMax) : undefined,
    })
    toggleBudget()
  }

  const handleRequirementAdd = () => {
    if (newRequirement.trim()) {
      onAddRequirement(newRequirement.trim())
      setNewRequirement('')
      toggleRequirement()
    }
  }

  return (
    <Box
      borderWidth="1px"
      borderColor="var(--core-color-border-default)"
      borderRadius="lg"
      bg="var(--core-color-surface-canvas)"
      p={6}
    >
      <VStack align="stretch" gap={4}>
        <HStack justify="space-between">
          <Box>
            <Text fontSize="md" fontWeight="semibold" color="var(--core-color-text-primary)">
              Intervention Controls
            </Text>
            <Text fontSize="sm" color="var(--core-color-text-muted)" mt={1}>
              Adjust parameters or take action during negotiation
            </Text>
          </Box>
          <Settings className="h-5 w-5" style={{ color: 'var(--core-color-text-muted)' }} />
        </HStack>

        {/* Budget Adjustment */}
        <Box>
          <Button
            size="sm"
            variant="outline"
            onClick={toggleBudget}
            w="full"
            justifyContent="start"
          >
            <HStack gap={2}>
              <DollarSign className="h-4 w-4" />
              <span>Adjust Budget Ceiling</span>
            </HStack>
          </Button>
          {isBudgetOpen && (
            <Box
              mt={3}
              p={4}
              borderRadius="md"
              bg="var(--core-color-surface-subtle)"
              borderWidth="1px"
              borderColor="var(--core-color-border-subtle)"
            >
              <VStack align="stretch" gap={3}>
                <Box>
                  <Text fontSize="sm" fontWeight="medium" color="var(--core-color-text-primary)" mb={2}>
                    Maximum Budget
                  </Text>
                  <Input
                    type="number"
                    value={budgetMax}
                    onChange={(e) => setBudgetMax(e.target.value)}
                    placeholder="e.g., 50000"
                    size="sm"
                  />
                </Box>
                <Box>
                  <Text fontSize="sm" fontWeight="medium" color="var(--core-color-text-primary)" mb={2}>
                    Minimum Budget (optional)
                  </Text>
                  <Input
                    type="number"
                    value={budgetMin}
                    onChange={(e) => setBudgetMin(e.target.value)}
                    placeholder="e.g., 30000"
                    size="sm"
                  />
                </Box>
                <HStack gap={2}>
                  <Button size="sm" colorPalette="blue" onClick={handleBudgetSave}>
                    Save
                  </Button>
                  <Button size="sm" variant="ghost" onClick={toggleBudget}>
                    Cancel
                  </Button>
                </HStack>
              </VStack>
            </Box>
          )}
        </Box>

        {/* Add Requirement */}
        <Box>
          <Button
            size="sm"
            variant="outline"
            onClick={toggleRequirement}
            w="full"
            justifyContent="start"
          >
            <HStack gap={2}>
              <Plus className="h-4 w-4" />
              <span>Add Requirement</span>
            </HStack>
          </Button>
          {isRequirementOpen && (
            <Box
              mt={3}
              p={4}
              borderRadius="md"
              bg="var(--core-color-surface-subtle)"
              borderWidth="1px"
              borderColor="var(--core-color-border-subtle)"
            >
              <VStack align="stretch" gap={3}>
                <Box>
                  <Text fontSize="sm" fontWeight="medium" color="var(--core-color-text-primary)" mb={2}>
                    New Requirement
                  </Text>
                  <Textarea
                    value={newRequirement}
                    onChange={(e) => setNewRequirement(e.target.value)}
                    placeholder="e.g., Must support SSO/SAML authentication"
                    size="sm"
                    rows={3}
                  />
                  <Text fontSize="xs" color="var(--core-color-text-muted)" mt={1}>
                    Agents will re-evaluate offers with this new requirement
                  </Text>
                </Box>
                <HStack gap={2}>
                  <Button size="sm" colorScheme="blue" onClick={handleRequirementAdd}>
                    Add
                  </Button>
                  <Button size="sm" variant="ghost" onClick={toggleRequirement}>
                    Cancel
                  </Button>
                </HStack>
              </VStack>
            </Box>
          )}
        </Box>

        {/* Pause Negotiations */}
        <Button
          size="sm"
          variant="outline"
          onClick={onPauseNegotiations}
          w="full"
          justifyContent="start"
          colorPalette="yellow"
        >
          <HStack gap={2}>
            <Pause className="h-4 w-4" />
            <span>Pause All Negotiations</span>
          </HStack>
        </Button>

        {/* Accept Best Offer */}
        {canAccept && bestSessionId && (
          <Box
            p={3}
            borderRadius="md"
            bg="green.subtle"
            borderWidth="1px"
            borderColor="green.emphasized"
          >
            <Text fontSize="sm" fontWeight="medium" color="green.fg" mb={2}>
              ✓ Best offer identified
            </Text>
            <Button
              size="sm"
              onClick={() => onAcceptOffer(bestSessionId)}
              w="full"
              colorPalette="green"
            >
              <HStack gap={2}>
                <CheckCircle className="h-4 w-4" />
                <span>Accept Best Offer</span>
              </HStack>
            </Button>
          </Box>
        )}

        {/* Quick Actions Info */}
        <Box
          p={3}
          borderRadius="md"
          bg="blue.subtle"
          borderWidth="1px"
          borderColor="blue.emphasized"
        >
          <Text fontSize="xs" color="blue.fg">
            💡 <strong>Tip:</strong> All interventions are logged in the audit trail and agents
            will immediately adapt their strategy based on your input.
          </Text>
        </Box>
      </VStack>
    </Box>
  )
}
