import { type ReactNode } from 'react'
import { Button as ChakraButton, type ButtonProps as ChakraButtonProps } from '@chakra-ui/react'

interface ButtonProps
  extends Omit<ChakraButtonProps, 'variant' | 'size' | 'isLoading' | 'width'> {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
  loading?: boolean
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  ...props
}: ButtonProps) {
  const colorScheme =
    variant === 'primary'
      ? 'primary'
      : variant === 'secondary'
        ? 'secondary'
        : variant === 'danger'
          ? 'red'
          : undefined
  const chakraVariant =
    variant === 'outline' ? 'outline' : variant === 'ghost' ? 'ghost' : 'solid'
  const chakraSize = size === 'sm' ? 'sm' : size === 'lg' ? 'lg' : 'md'

  return (
    <ChakraButton
      colorScheme={colorScheme}
      variant={chakraVariant}
      size={chakraSize}
      width={fullWidth ? '100%' : undefined}
      loading={loading}
      {...props}
    >
      {children}
    </ChakraButton>
  )
}
