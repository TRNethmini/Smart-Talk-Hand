import * as React from "react";
import { View, Text, ViewProps } from "react-native";
import { cn } from "../../lib/utils";

export function Avatar({ className, ...props }: ViewProps) {
    return (
        <View
            className={cn("relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full", className)}
            {...props}
        />
    );
}

export function AvatarFallback({ className, ...props }: ViewProps & { children: React.ReactNode }) {
    return (
        <View
            className={cn("flex h-full w-full items-center justify-center rounded-full bg-muted", className)}
            {...props}
        >
            {typeof props.children === 'string' ? <Text>{props.children}</Text> : props.children}
        </View>
    );
}
