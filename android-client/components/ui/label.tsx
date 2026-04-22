import { Text, TextProps } from "react-native";
import { cn } from "../../lib/utils";

export function Label({ className, ...props }: TextProps) {
    return (
        <Text
            className={cn(
                "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-foreground",
                className
            )}
            {...props}
        />
    );
}
