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
          borderWidth="1px"
          borderColor="gray.200"
          bg="white"
          p={2}
          rounded="0"
          _dark={{ borderColor: '#262626', bg: '#0F0F0F' }}
          _focusWithin={{
            borderColor: 'primary.500',
            boxShadow: { base: '0 0 0 2px rgba(37, 99, 235, 0.35)', _dark: '0 0 0 2px rgba(59, 130, 246, 0.35)' },
          }}
        >
          <Input
            type="text"
            value={value}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setValue(e.target.value)}
            placeholder="Need 200 design seats · Budget $1,000/seat/year · SOC2 required"
            variant="outline"
            py={2}
            fontSize="md"
            border="none"
            color="gray.900"
            _dark={{ color: '#FAFAFA' }}
            _placeholder={{ color: 'gray.500', _dark: { color: '#71717A' } }}
            _focus={{ border: 'none', boxShadow: 'none' }}
          />
          <Button
            type="submit"
            disabled={!value.trim()}
            height={11}
            bgGradient="linear(to-r, teal.400, cyan.400)"
            color="white"
            _hover={{ bgGradient: 'linear(to-r, teal.500, cyan.500)' }}
          >
            Describe <Icon as={ArrowRight} boxSize={4} ml={2} />
          </Button>
        </HStack>
      </form>
    </Box>
  )
}
