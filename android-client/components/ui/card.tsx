import { View, ViewProps, Text, TextProps } from "react-native";
import { cn } from "../../lib/utils";

export function Card({ className, ...props }: ViewProps) {
    return (
        <View
            className={cn(
                "rounded-xl border border-border bg-card shadow-sm",
                className
            )}
            {...props}
        />
    );
}

export function CardHeader({ className, ...props }: ViewProps) {
    return (
        <View
            className={cn("flex flex-col space-y-1.5 p-6", className)}
            {...props}
        />
    );
}

export function CardTitle({ className, ...props }: TextProps) {
    return (
        <Text
            className={cn(
                "text-2xl font-semibold leading-none tracking-tight text-card-foreground",
                className
            )}
            {...props}
        />
    );
}

export function CardContent({ className, ...props }: ViewProps) {
    return <View className={cn("p-6 pt-0", className)} {...props} />;
}
