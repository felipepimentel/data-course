import React from 'react';
import { cn } from '../../lib/utils';

type AlertVariant = 'default' | 'destructive' | 'success' | 'warning';

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: AlertVariant;
}

export const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
    ({ className, variant = 'default', ...props }, ref) => {
        const variantClasses = {
            default: 'bg-blue-50 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300',
            destructive: 'bg-red-50 text-red-800 dark:bg-red-900/20 dark:text-red-300',
            success: 'bg-green-50 text-green-800 dark:bg-green-900/20 dark:text-green-300',
            warning: 'bg-yellow-50 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300',
        };

        return (
            <div
                ref={ref}
                role="alert"
                className={cn(
                    'flex items-center p-4 rounded-md border',
                    {
                        'border-blue-200 dark:border-blue-800': variant === 'default',
                        'border-red-200 dark:border-red-800': variant === 'destructive',
                        'border-green-200 dark:border-green-800': variant === 'success',
                        'border-yellow-200 dark:border-yellow-800': variant === 'warning',
                    },
                    variantClasses[variant],
                    className
                )}
                {...props}
            />
        );
    }
);

Alert.displayName = 'Alert'; 