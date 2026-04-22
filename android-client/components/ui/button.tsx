import { Text, Pressable, PressableProps, View } from "react-native";
import { cn } from "../../lib/utils";

interface ButtonProps extends PressableProps {
    variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link" | "gradient";
    size?: "default" | "sm" | "lg" | "icon";
    className?: string;
    children?: React.ReactNode;
    textClassName?: string;
}

export function Button({
    className,
    variant = "default",
    size = "default",
    children,
    textClassName,
    ...props
}: ButtonProps) {
    return (
        <Pressable
            className={cn(
                "justify-center items-center rounded-xl flex-row gap-2 active:opacity-80 transition-opacity",
                {
                    "bg-primary": variant === "default",
                    "bg-destructive": variant === "destructive",
                    "border border-input bg-background": variant === "outline",
                    "bg-secondary": variant === "secondary",
                    "bg-transparent": variant === "ghost",
                    "text-primary underline-offset-4": variant === "link",
                    "bg-gradient-to-r from-primary to-primary/80": variant === "gradient", // NativeWind might handle gradient differently, fallback to primary for now
                },
                {
                    "h-10 px-4 py-2": size === "default",
                    "h-9 rounded-md px-3": size === "sm",
                    "h-11 rounded-md px-8": size === "lg",
                    "h-10 w-10": size === "icon",
                },
                className
            )}
            {...props}
        >
            {typeof children === "string" ? (
                <Text
                    className={cn(
                        "text-sm font-medium",
                        {
                            "text-primary-foreground": variant === "default",
                            "text-destructive-foreground": variant === "destructive",
                            "text-accent-foreground": variant === "outline", // adjust as needed
                            "text-secondary-foreground": variant === "secondary",
                            "text-primary": variant === "ghost" || variant === "link" || variant === "outline",
                        },
                        textClassName
                    )}
                >
                    {children}
                </Text>
            ) : (
                children
            )}
        </Pressable>
    );
}
