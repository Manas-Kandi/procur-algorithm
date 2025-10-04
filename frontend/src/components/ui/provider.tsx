import { ReactNode } from 'react'
import { ChakraProvider, defaultSystem } from '@chakra-ui/react'
import { ThemeProvider as LegacyTokensProvider } from '../../ui/theme/ThemeProvider'
import { ColorModeProvider } from '@/components/ui/color-mode'

export function Provider({ children }: { children: ReactNode }) {
  return (
    <ColorModeProvider defaultTheme="dark">
      <ChakraProvider value={defaultSystem}>
        {/* Keep legacy CSS variables available while migrating components to Chakra */}
        <LegacyTokensProvider>
          {children}
        </LegacyTokensProvider>
      </ChakraProvider>
    </ColorModeProvider>
  )
}
