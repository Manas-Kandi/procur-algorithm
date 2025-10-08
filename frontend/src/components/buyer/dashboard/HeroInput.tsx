import { useState, type FormEvent, type ChangeEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { Box, HStack, Input, Button, Icon } from '@chakra-ui/react'

interface HeroInputProps {
  onSubmit?: (description: string) => void
}

export function HeroInput({ onSubmit }: HeroInputProps) {
  const navigate = useNavigate()
  const [value, setValue] = useState('')
  // Static colors with dark-mode overrides handled via _dark props

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (value.trim()) {
      if (onSubmit) {
        onSubmit(value)
      } else {
        // Navigate to new request with pre-filled description
        void navigate('/requests/new', { state: { description: value } })
      }
    }
  }

  return (
    <Box>
      <form onSubmit={handleSubmit}>
        <HStack
          gap={3}
          bg="bg.subtle"
          px={3}
          py={2}
          borderRadius="lg"
          borderWidth="1px"
          borderColor="transparent"
          transition="background-color 0.2s ease, border-color 0.2s ease"
          _focusWithin={{ bg: 'bg.panel', borderColor: 'border' }}
        >
          <Input
            type="text"
            value={value}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setValue(e.target.value)}
            placeholder="Describe what you need (e.g., 200 design seats, SOC2, $1k/seat/yr)"
            variant="subtle"
            py={2}
            fontSize="md"
            color="fg"
            _placeholder={{ color: 'fg.muted' }}
          />
          <Button
            type="submit"
            size="sm"
            colorPalette="blue"
            disabled={!value.trim()}
          >
            <HStack gap={2}>
              <span>Describe</span>
              <Icon as={ArrowRight} boxSize={4} />
            </HStack>
          </Button>
        </HStack>
      </form>
    </Box>
  )
}

