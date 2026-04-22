import { View, Text, Image } from "react-native";
import { useRouter } from "expo-router";
import { Button } from "../components/ui/button";
import { Hand } from "lucide-react-native";
import { SafeAreaView } from "react-native-safe-area-context";

export default function Welcome() {
    const router = useRouter();

    return (
        <SafeAreaView className="flex-1 bg-background">
            <View className="flex-1 flex-col items-center justify-center px-6">
                <View className="max-w-md w-full space-y-8 items-center">
                    {/* Logo */}
                    <View className="flex justify-center mb-8">
                        <View className="bg-white p-6 rounded-3xl shadow-sm">
                            <Hand size={64} className="text-primary" color="#14b8a6" />
                        </View>
                    </View>

                    {/* Hero Image */}
                    <View className="rounded-3xl overflow-hidden shadow-sm w-full h-48 mb-8">
                        <Image
                            source={require("../assets/hero-hands.png")}
                            className="w-full h-full"
                            resizeMode="cover"
                        />
                    </View>

                    {/* Title */}
                    <View className="space-y-3 items-center mb-8">
                        <Text className="text-4xl font-bold text-foreground text-center">
                            Smart TalkHand
                        </Text>
                        <Text className="text-lg text-muted-foreground text-center">
                            Learn Sri Lankan Sign Language with AI-powered guidance
                        </Text>
                    </View>

                    {/* CTA */}
                    <View className="space-y-4 w-full pt-4 items-center">
                        <Button
                            variant="default" // Gradient generic fallback
                            size="lg"
                            className="w-full bg-primary"
                            onPress={() => router.push("/login")}
                        >
                            Get Started
                        </Button>

                        <Text className="text-sm text-muted-foreground text-center mt-4">
                            Join our inclusive learning community
                        </Text>
                    </View>
                </View>
            </View>
        </SafeAreaView>
    );
}
