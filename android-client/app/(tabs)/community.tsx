import { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, ScrollView, RefreshControl } from "react-native";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { Card } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Avatar } from "../../components/ui/avatar";
import {
    ArrowLeft,
    Heart,
    MessageCircle,
    Share2,
    Trophy,
    Star,
    TrendingUp
} from "lucide-react-native";
import { apiService } from "../../services/api";

type Post = {
    id: string;
    user: string;
    initials: string;
    achievement: string;
    time: string;
    likes: number;
    comments: number;
    badge: string;
};

export default function Community() {
    const router = useRouter();
    const [posts, setPosts] = useState<Post[]>([]);
    const [refreshing, setRefreshing] = useState(false);

    const loadPosts = async () => {
        try {
            const data = await apiService.get('/api/v1/community/posts');
            setPosts(data);
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        loadPosts();
    }, []);

    const onRefresh = async () => {
        setRefreshing(true);
        await loadPosts();
        setRefreshing(false);
    };

    const handleShare = async () => {
        try {
            await apiService.post('/api/v1/community/share', {
                achievement: "Crushing my daily goals! 🌟",
                badge: "fire"
            });
            await loadPosts();
        } catch (e) {
            console.error("Failed to share", e);
        }
    };

    const getBadgeColor = (badge: string) => {
        switch (badge) {
            case "gold": return "bg-yellow-500";
            case "fire": return "bg-orange-500";
            case "heart": return "bg-pink-500";
            case "star": return "bg-purple-500";
            default: return "bg-primary";
        }
    };

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
                <Text className="text-lg font-semibold text-foreground">Community</Text>
                <View className="w-16" />
            </View>

            <ScrollView 
                contentContainerStyle={{ paddingBottom: 24 }}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
                }
            >
                {/* Main Content */}
                <View className="px-6 py-6 space-y-6 gap-6">
                    {/* Welcome Banner */}
                    <Card className="p-6 shadow-md rounded-3xl bg-primary overflow-hidden">
                        {/* Gradient mock via style or plain bg-primary */}
                        <View className="flex-row items-center gap-4">
                            <Trophy size={48} className="text-primary-foreground opacity-90" color="white" />
                            <View className="flex-1">
                                <Text className="text-xl font-bold mb-1 text-primary-foreground">Celebrate Together</Text>
                                <Text className="text-primary-foreground/90 text-sm">
                                    Share your achievements and motivate others
                                </Text>
                            </View>
                        </View>
                    </Card>

                    {/* Stats */}
                    <View className="flex-row gap-3">
                        <Card className="p-4 shadow-sm rounded-2xl flex-1 items-center bg-card">
                            <TrendingUp size={24} className="text-primary mb-2" color="#14b8a6" />
                            <Text className="text-2xl font-bold text-primary">1.2k</Text>
                            <Text className="text-xs text-muted-foreground text-center">Active Learners</Text>
                        </Card>
                        <Card className="p-4 shadow-sm rounded-2xl flex-1 items-center bg-card">
                            <Star size={24} className="text-accent mb-2" color="#f97316" />
                            <Text className="text-2xl font-bold text-accent">350</Text>
                            <Text className="text-xs text-muted-foreground text-center">Posts Today</Text>
                        </Card>
                        <Card className="p-4 shadow-sm rounded-2xl flex-1 items-center bg-card">
                            <Heart size={24} className="text-pink-500 mb-2" color="#ec4899" />
                            <Text className="text-2xl font-bold text-pink-500">5.8k</Text>
                            <Text className="text-xs text-muted-foreground text-center">Encouraging</Text>
                        </Card>
                    </View>

                    {/* Posts Feed */}
                    <View className="space-y-4 gap-4">
                        <Text className="text-lg font-semibold px-1 text-foreground">Recent Achievements</Text>
                        {posts.map((post) => (
                            <Card key={post.id} className="p-5 shadow-sm rounded-3xl bg-card">
                                <View className="flex-row items-start gap-4">
                                    {/* Avatar with Badge */}
                                    <View className="relative">
                                        <Avatar className="w-12 h-12 bg-primary/10 items-center justify-center rounded-full">
                                            <Text className="text-primary font-semibold">{post.initials}</Text>
                                        </Avatar>
                                        <View className={`absolute -bottom-1 -right-1 w-5 h-5 ${getBadgeColor(post.badge)} rounded-full border-2 border-card items-center justify-center`}>
                                            {post.badge === "gold" && <Trophy size={10} color="white" />}
                                            {post.badge === "fire" && <Text className="text-[10px]">🔥</Text>}
                                            {post.badge === "heart" && <Heart size={10} color="white" fill="white" />}
                                            {post.badge === "star" && <Star size={10} color="white" fill="white" />}
                                        </View>
                                    </View>

                                    {/* Post Content */}
                                    <View className="flex-1">
                                        <View className="flex-row items-center justify-between mb-2">
                                            <Text className="font-semibold text-foreground">{post.user}</Text>
                                            <Text className="text-xs text-muted-foreground">{post.time}</Text>
                                        </View>
                                        <Text className="text-sm mb-4 text-foreground">{post.achievement}</Text>

                                        {/* Actions */}
                                        <View className="flex-row items-center gap-6">
                                            <TouchableOpacity className="flex-row items-center gap-2">
                                                <Heart size={16} className="text-muted-foreground" color="#64748b" />
                                                <Text className="text-sm text-muted-foreground">{post.likes}</Text>
                                            </TouchableOpacity>
                                            <TouchableOpacity
                                                className="flex-row items-center gap-2"
                                                onPress={() => router.push("/(tabs)/chat")}
                                            >
                                                <MessageCircle size={16} className="text-muted-foreground" color="#64748b" />
                                                <Text className="text-sm text-muted-foreground">{post.comments}</Text>
                                            </TouchableOpacity>
                                            <TouchableOpacity className="flex-row items-center gap-2">
                                                <Share2 size={16} className="text-muted-foreground" color="#64748b" />
                                            </TouchableOpacity>
                                        </View>
                                    </View>
                                </View>
                            </Card>
                        ))}
                    </View>

                    {/* Share Achievement Button */}
                    <Button
                        variant="default"
                        size="lg"
                        className="w-full flex-row gap-2 bg-primary"
                        onPress={handleShare}
                    >
                        <Trophy size={20} className="text-primary-foreground" color="white" />
                        <Text className="text-primary-foreground">Share Your Achievement</Text>
                    </Button>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}
