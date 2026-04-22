import { View, ViewProps } from "react-native";
import { cn } from "../../lib/utils";

interface ProgressProps extends ViewProps {
    value?: number;
    className?: string;
    indicatorClassName?: string;
}

export function Progress({ className, value = 0, indicatorClassName, ...props }: ProgressProps) {
    return (
        <View
            className={cn(
                "relative h-4 w-full overflow-hidden rounded-full bg-secondary",
                className
            )}
            {...props}
        >
            <View
                className={cn("h-full w-full flex-1 bg-primary transition-all rounded-full", indicatorClassName)}
                style={{ width: `${value || 0}%` }}
            />
        </View>
    );
}
