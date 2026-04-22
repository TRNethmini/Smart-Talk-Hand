import { View, Text, TouchableOpacity, ScrollView, Switch } from "react-native";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { useAuth } from "../../context/AuthContext";
import { Card } from "../../components/ui/card";
import { Avatar } from "../../components/ui/avatar";
import {
    ArrowLeft,
    User,
    Bell,
    Globe,
    Moon,
    Shield,
    HelpCircle,
    LogOut,
    ChevronRight
} from "lucide-react-native";

export default function Settings() {
    const router = useRouter();
    const { user, logout } = useAuth();

    return (
        <SafeAreaView className="flex-1 bg-background" edges={['top']}>
            {/* Header */}
            <View className="bg-background/80 blur-md border-b border-border z-10 px-6 py-4 flex-row items-center justify-between">
                <TouchableOpacity
                    onPress={() => router.push("/(tabs)")}
                    className="flex-row items-center gap-2"
                >
                    <ArrowLeft size={20} className="text-muted-foreground" color="#64748b" />
                    <Text className="text-muted-foreground">Back</Text>
                </TouchableOpacity>
                <Text className="text-lg font-semibold text-foreground">Settings</Text>
                <View className="w-16" />
            </View>

            <ScrollView contentContainerStyle={{ paddingBottom: 24 }}>
                {/* Main Content */}
                <View className="px-6 py-6 space-y-6 gap-6 pb-8">
                    {/* Profile Section */}
                    <Card className="p-6 shadow-md rounded-3xl bg-card">
                        <View className="flex-row items-center gap-4">
                            <Avatar className="w-16 h-16 bg-primary/10 items-center justify-center rounded-full">
                                <Text className="text-primary font-bold text-xl">{user?.initials || "JD"}</Text>
                            </Avatar>
                            <View className="flex-1">
                                <Text className="text-xl font-bold text-foreground">{user?.name || "John Doe"}</Text>
                                <Text className="text-sm text-muted-foreground">{user?.email || "guest@talkhand.com"}</Text>
                            </View>
                            <TouchableOpacity className="p-2">
                                <User size={20} className="text-primary" color="#14b8a6" />
                            </TouchableOpacity>
                        </View>
                    </Card>

                    {/* Preferences */}
                    <View className="space-y-3 gap-3">
                        <Text className="text-lg font-semibold px-1 text-foreground">Preferences</Text>

                        <Card className="p-5 shadow-sm rounded-3xl bg-card">
                            <View className="flex-row items-center justify-between">
                                <View className="flex-row items-center gap-3">
                                    <View className="bg-primary/10 p-2 rounded-xl">
                                        <Bell size={20} className="text-primary" color="#14b8a6" />
                                    </View>
                                    <View>
                                        <Text className="text-base font-medium text-foreground">Notifications</Text>
                                        <Text className="text-xs text-muted-foreground">Get learning reminders</Text>
                                    </View>
                                </View>
                                <Switch value={true} trackColor={{ true: "#14b8a6" }} />
                            </View>
                        </Card>

                        <Card className="p-5 shadow-sm rounded-3xl bg-card">
                            <View className="flex-row items-center justify-between">
                                <View className="flex-row items-center gap-3">
                                    <View className="bg-primary/10 p-2 rounded-xl">
                                        <Moon size={20} className="text-primary" color="#14b8a6" />
                                    </View>
                                    <View>
                                        <Text className="text-base font-medium text-foreground">Dark Mode</Text>
                                        <Text className="text-xs text-muted-foreground">Reduce eye strain</Text>
                                    </View>
                                </View>
                                <Switch value={false} trackColor={{ true: "#14b8a6" }} />
                            </View>
                        </Card>

                        <Card className="p-5 shadow-sm rounded-3xl bg-card">
                            <View className="flex-row items-center justify-between">
                                <View className="flex-row items-center gap-3">
                                    <View className="bg-primary/10 p-2 rounded-xl">
                                        <Globe size={20} className="text-primary" color="#14b8a6" />
                                    </View>
                                    <View>
                                        <Text className="text-base font-medium text-foreground">Language</Text>
                                        <Text className="text-xs text-muted-foreground">English</Text>
                                    </View>
                                </View>
                                <ChevronRight size={20} className="text-muted-foreground" color="#64748b" />
                            </View>
                        </Card>
                    </View>

                    {/* Privacy & Safety */}
                    <View className="space-y-3 gap-3">
                        <Text className="text-lg font-semibold px-1 text-foreground">Privacy & Safety</Text>

                        <Card className="p-5 shadow-sm rounded-3xl bg-card">
                            <View className="flex-row items-center justify-between">
                                <View className="flex-row items-center gap-3">
                                    <View className="bg-accent/10 p-2 rounded-xl">
                                        <Shield size={20} className="text-accent" color="#f97316" />
                                    </View>
                                    <View>
                                        <Text className="text-base font-medium text-foreground">Privacy Settings</Text>
                                        <Text className="text-xs text-muted-foreground">Control your data and visibility</Text>
                                    </View>
                                </View>
                                <ChevronRight size={20} className="text-muted-foreground" color="#64748b" />
                            </View>
                        </Card>

                        <Card className="p-5 shadow-sm rounded-3xl bg-card">
                            <View className="flex-row items-center justify-between">
                                <View className="flex-row items-center gap-3">
                                    <View className="bg-accent/10 p-2 rounded-xl">
                                        <Shield size={20} className="text-accent" color="#f97316" />
                                    </View>
                                    <View>
                                        <Text className="text-base font-medium text-foreground">Safety Mode</Text>
                                        <Text className="text-xs text-muted-foreground">Filter inappropriate content</Text>
                                    </View>
                                </View>
                                <Switch value={true} trackColor={{ true: "#14b8a6" }} />
                            </View>
                        </Card>
                    </View>

                    {/* Support */}
                    <View className="space-y-3 gap-3">
                        <Text className="text-lg font-semibold px-1 text-foreground">Support</Text>

                        <Card className="p-5 shadow-sm rounded-3xl bg-card">
                            <View className="flex-row items-center justify-between">
                                <View className="flex-row items-center gap-3">
                                    <View className="bg-secondary p-2 rounded-xl">
                                        <HelpCircle size={20} className="text-primary" color="#14b8a6" />
                                    </View>
                                    <View>
                                        <Text className="text-base font-medium text-foreground">Help & Support</Text>
                                        <Text className="text-xs text-muted-foreground">Get assistance and FAQs</Text>
                                    </View>
                                </View>
                                <ChevronRight size={20} className="text-muted-foreground" color="#64748b" />
                            </View>
                        </Card>
                    </View>

                    {/* Logout */}
                    <TouchableOpacity onPress={async () => {
                        await logout();
                        router.replace("/login");
                    }}>
                        <Card className="p-5 shadow-sm rounded-3xl bg-card flex-row items-center justify-center gap-3">
                            <LogOut size={20} className="text-destructive" color="#ef4444" />
                            <Text className="font-medium text-destructive">Log Out</Text>
                        </Card>
                    </TouchableOpacity>

                    {/* App Version */}
                    <Text className="text-center text-xs text-muted-foreground pt-4">
                        Smart TalkHand v1.0.0
                    </Text>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}
