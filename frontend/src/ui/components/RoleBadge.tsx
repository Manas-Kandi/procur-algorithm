import clsx from 'clsx'

export type RoleVariant = 'Buyer' | 'Seller' | 'Admin'

const ROLE_COLOR_CLASS: Record<RoleVariant, string> = {
  Buyer: 'role-badge-buyer',
  Seller: 'role-badge-seller',
  Admin: 'role-badge-admin'
}

interface RoleBadgeProps {
  role: RoleVariant
}

export function RoleBadge ({ role }: RoleBadgeProps): JSX.Element {
  return (
    <span className={clsx('role-badge', ROLE_COLOR_CLASS[role])}>
      {role}
    </span>
  )
}
