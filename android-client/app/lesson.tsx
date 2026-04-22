import { View, Text, TouchableOpacity, ScrollView } from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { ArrowLeft, PlayCircle, Video } from "lucide-react-native";

export default function LessonModule() {
    const router = useRouter();
    const params = useLocalSearchParams();
    const modelName = (params.model as string) || "Unknown Model";
    const targetSign = (params.target as string) || "Unknown Sign";

    return (
        <SafeAreaView className="flex-1 bg-background" edges={['top']}>
            {/* Header */}
            <View className="bg-background/80 blur-md border-b border-border z-10 px-6 py-4">
                <View className="flex-row items-center justify-between mb-3">
                    <TouchableOpacity
                        onPress={() => router.back()}
                        className="flex-row items-center gap-2"
                    >
                        <ArrowLeft size={20} color="#64748b" />
                        <Text className="text-muted-foreground">Back to classes</Text>
                    </TouchableOpacity>
                    <Text className="text-sm font-medium text-primary">
                        {modelName.replace("ssl_", "").toUpperCase()}
                    </Text>
                </View>
            </View>

            <ScrollView contentContainerStyle={{ paddingBottom: 24 }}>
                <View className="px-6 py-6 space-y-6 gap-6">
                    {/* Lesson Card */}
                    <Card className="p-8 shadow-sm rounded-3xl bg-card items-center">
                        <View className="space-y-6 w-full items-center">
                            {/* Sign Animation Area */}
                            <View className="bg-gradient-to-br from-secondary/30 to-primary/10 rounded-3xl p-12 items-center justify-center w-full aspect-square bg-secondary">
                                <Text className="text-8xl text-foreground font-bold">{targetSign}</Text>
                            </View>

                            {/* Sign Details */}
                            <View className="space-y-2 items-center">
                                <Text className="text-3xl font-bold text-foreground">Sign: {targetSign}</Text>
                                <Text className="text-lg text-muted-foreground text-center px-4">
                                    Get ready to practice this sign using your camera!
                                </Text>
                            </View>

                            {/* Play Demo Button */}
                            <Button
                                variant="default"
                                size="lg"
                                className="w-full flex-row gap-2 bg-primary mt-4"
                                onPress={() => router.push(`/gesture-learning?model=${encodeURIComponent(modelName)}&target=${encodeURIComponent(targetSign)}`)}
                            >
                                <Video size={20} color="white" />
                                <Text className="text-primary-foreground ml-2 font-semibold">Start AI Practice</Text>
                            </Button>
                        </View>
                    </Card>

                    {/* Instructions */}
                    <Card className="p-6 shadow-sm rounded-3xl bg-card">
                        <Text className="text-lg font-semibold mb-4 text-foreground">How to Practice</Text>
                        <View className="space-y-4 gap-3">
                            <View className="flex-row items-center gap-3">
                                <View className="w-8 h-8 rounded-full bg-primary/20 items-center justify-center">
                                    <Text className="text-sm font-bold text-primary">1</Text>
                                </View>
                                <Text className="text-sm text-foreground flex-1">Pro tip: Ensure your environment is well lit</Text>
                            </View>
                            <View className="flex-row items-center gap-3">
                                <View className="w-8 h-8 rounded-full bg-primary/20 items-center justify-center">
                                    <Text className="text-sm font-bold text-primary">2</Text>
                                </View>
                                <Text className="text-sm text-foreground flex-1">Perform the hand gesture steadily in frame</Text>
                            </View>
                            <View className="flex-row items-center gap-3">
                                <View className="w-8 h-8 rounded-full bg-primary/20 items-center justify-center">
                                    <Text className="text-sm font-bold text-primary">3</Text>
                                </View>
                                <Text className="text-sm text-foreground flex-1">Press Start Capture and hold for 3 seconds</Text>
                            </View>
                        </View>
                    </Card>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}
