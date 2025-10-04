import { ReactNode } from 'react'
import { ChakraProvider } from '@chakra-ui/react'
import { ThemeProvider as LegacyTokensProvider } from '../../ui/theme/ThemeProvider'
import { ColorModeProvider, DarkMode } from '@/components/ui/color-mode'
import { system } from './chakra-system'

export function Provider({ children }: { children: ReactNode }) {
  return (
    <ChakraProvider value={system}>
      <ColorModeProvider defaultTheme="dark">
        {/* Keep legacy CSS variables available while migrating components to Chakra */}
        <LegacyTokensProvider>
          <DarkMode>
            {children}
          </DarkMode>
        </LegacyTokensProvider>
      </ColorModeProvider>
    </ChakraProvider>
  )
}
