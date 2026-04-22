import { TextInput, TextInputProps, View } from "react-native";
import { cn } from "../../lib/utils";

export interface InputProps extends TextInputProps {
    className?: string;
}

export function Input({ className, ...props }: InputProps) {
    return (
        <TextInput
            className={cn(
                "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
                className
            )}
            placeholderTextColor="#9ca3af" // muted-foreground equivalent roughly
            {...props}
        />
    );
}
