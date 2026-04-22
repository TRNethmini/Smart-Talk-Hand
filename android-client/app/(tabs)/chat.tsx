import { useState, useEffect, useRef } from "react";
import { View, Text, TouchableOpacity, ScrollView, TextInput, KeyboardAvoidingView, Platform } from "react-native";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { Card } from "../../components/ui/card";
import { Input } from "../../components/ui/input";
import { Button } from "../../components/ui/button";
import {
    ArrowLeft,
    Search,
    Send,
    Smile,
    MoreVertical,
    Circle,
    Flag
} from "lucide-react-native";
import { Avatar } from "@/components/ui/avatar";
import { apiService } from "../../services/api";
import { useAuth } from "../../context/AuthContext";

type ChatPreview = {
    id: string;
    name: string;
    initials: string;
    lastMessage: string;
    time: string;
    unread: number;
    online: boolean;
};

type Message = {
    id: string;
    sender: "me" | "them";
    text: string;
    time: string;
};

export default function Chat() {
    const router = useRouter();
    const { user } = useAuth();
    const [view, setView] = useState<"list" | "chat">("list");
    const [activeChat, setActiveChat] = useState<ChatPreview | null>(null);
    const [message, setMessage] = useState("");
    
    const [chats, setChats] = useState<ChatPreview[]>([]);
    const [messages, setMessages] = useState<Message[]>([]);
    const scrollRef = useRef<ScrollView>(null);

    const loadChats = async () => {
        try {
            const data = await apiService.get('/api/v1/chat/conversations');
            setChats(data);
        } catch (e) {
            console.error(e);
        }
    };

    const loadMessages = async (chatId: string) => {
        if (!chatId) return;
        try {
            const data = await apiService.get(`/api/v1/chat/${chatId}/messages`);
            setMessages(data);
            setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 100);
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        if (view === "list") {
            loadChats();
        } else if (view === "chat" && activeChat) {
            loadMessages(activeChat.id);
            // Optionally set up an interval for polling here
            const interval = setInterval(() => loadMessages(activeChat.id), 5000);
            return () => clearInterval(interval);
        }
    }, [view, activeChat]);

    const handleSendMessage = async () => {
        if (!message.trim() || !activeChat) return;
        try {
            await apiService.post(`/api/v1/chat/${activeChat.id}/send`, { text: message.trim() });
            setMessage("");
            await loadMessages(activeChat.id);
        } catch (e) {
            console.error(e);
        }
    };

    if (view === "chat") {
        return (
            <SafeAreaView className="flex-1 bg-background" edges={['top']}>
                <KeyboardAvoidingView
                    behavior={Platform.OS === "ios" ? "padding" : undefined}
                    className="flex-1"
                    keyboardVerticalOffset={Platform.OS === "ios" ? 60 : 0}
                >
                    <View className="flex-1 flex-col">
                        {/* Chat Header */}
                        <View className="bg-background/95 blur-md border-b border-border px-6 py-4 flex-row items-center justify-between z-10">
                            <View className="flex-row items-center gap-3">
                                <TouchableOpacity
                                    onPress={() => setView("list")}
                                    className="p-1"
                                >
                                    <ArrowLeft size={20} className="text-muted-foreground" color="#64748b" />
                                </TouchableOpacity>
                                <Avatar className="w-10 h-10 bg-primary/10 items-center justify-center rounded-full">
                                    <Text className="text-primary font-semibold">{activeChat?.initials}</Text>
                                </Avatar>
                                <View>
                                    <Text className="font-semibold text-foreground">{activeChat?.name}</Text>
                                    <View className="flex-row items-center gap-1.5">
                                        {activeChat?.online && <View className="w-2 h-2 bg-green-500 rounded-full" />}
                                        <Text className="text-xs text-muted-foreground">{activeChat?.online ? 'Online' : 'Offline'}</Text>
                                    </View>
                                </View>
                            </View>
                            <TouchableOpacity className="p-1">
                                <MoreVertical size={20} className="text-muted-foreground" color="#64748b" />
                            </TouchableOpacity>
                        </View>

                        {/* Messages */}
                        <ScrollView ref={scrollRef} className="flex-1 px-6 py-6" contentContainerStyle={{ gap: 16 }}>
                            {messages.map((msg) => (
                                <View
                                    key={msg.id}
                                    className={`flex-row ${msg.sender === "me" ? "justify-end" : "justify-start"}`}
                                >
                                    <View
                                        className={`max-w-[80%] rounded-3xl px-5 py-3 ${msg.sender === "me"
                                                ? "bg-primary rounded-tr-sm"
                                                : "bg-card shadow-sm rounded-tl-sm"
                                            }`}
                                    >
                                        <Text className={`text-sm ${msg.sender === "me" ? "text-primary-foreground" : "text-foreground"}`}>
                                            {msg.text}
                                        </Text>
                                        <Text className={`text-xs mt-1 ${msg.sender === "me" ? "text-primary-foreground/70" : "text-muted-foreground"
                                            }`}>
                                            {msg.time}
                                        </Text>
                                    </View>
                                </View>
                            ))}
                            <Text className="text-center text-xs text-muted-foreground py-2">
                                typing...
                            </Text>
                        </ScrollView>

                        {/* Input Area */}
                        <View className="bg-background/95 blur-md border-t border-border px-6 py-4 pb-8">
                            <View className="flex-row items-center gap-3">
                                <TouchableOpacity className="p-2">
                                    <Smile size={24} className="text-muted-foreground" color="#64748b" />
                                </TouchableOpacity>
                                <Input
                                    value={message}
                                    onChangeText={setMessage}
                                    placeholder="Type a message..."
                                    className="flex-1 h-12 rounded-full border-input bg-card"
                                />
                                <Button
                                    size="icon"
                                    className="rounded-full w-12 h-12 bg-primary items-center justify-center p-0"
                                    onPress={handleSendMessage}
                                >
                                    <Send size={20} className="text-primary-foreground" color="#fff" />
                                </Button>
                            </View>
                        </View>
                    </View>
                </KeyboardAvoidingView>
            </SafeAreaView>
        );
    }

    return (
        <SafeAreaView className="flex-1 bg-background" edges={['top']}>
            {/* Header */}
            <View className="bg-background/80 blur-md border-b border-border z-10 px-6 py-4">
                <View className="flex-row items-center justify-between mb-4">
                    <View className="items-center flex-row gap-2 invisible">
                        {/* Spacer to match back button if needed, or back to dashboard */}
                        <TouchableOpacity
                            onPress={() => router.push("/(tabs)")}
                            className="flex-row items-center gap-2"
                        >
                            <ArrowLeft size={20} className="text-muted-foreground" color="#64748b" />
                            <Text className="text-muted-foreground">Back</Text>
                        </TouchableOpacity>
                    </View>
                    <Text className="text-lg font-semibold text-foreground">Messages</Text>
                    <View className="w-16" />
                </View>

                {/* Search */}
                <View className="relative justify-center">
                    <View className="absolute left-3 z-10">
                        <Search size={20} className="text-muted-foreground" color="#9ca3af" />
                    </View>
                    <Input
                        placeholder="Search conversations..."
                        className="pl-10 h-12 rounded-full border-input bg-card"
                    />
                </View>
            </View>

            <ScrollView contentContainerStyle={{ paddingBottom: 24 }}>
                {/* Chats List */}
                <View className="px-6 py-6 space-y-3 gap-3">
                    {chats.map((chat) => (
                        <TouchableOpacity
                            key={chat.id}
                            onPress={() => {
                                setActiveChat(chat);
                                setView("chat");
                            }}
                            activeOpacity={0.7}
                        >
                            <Card className="p-5 shadow-sm rounded-3xl bg-card flex-row items-center gap-4">
                                <View className="relative">
                                    <Avatar className="w-14 h-14 bg-primary/10 items-center justify-center rounded-full">
                                        <Text className="text-primary font-semibold text-lg">{chat.initials}</Text>
                                    </Avatar>
                                    {chat.online && (
                                        <View className="absolute bottom-0 right-0 w-4 h-4 bg-green-500 border-2 border-card rounded-full" />
                                    )}
                                </View>

                                <View className="flex-1">
                                    <View className="flex-row items-center justify-between mb-1">
                                        <Text className="font-semibold text-foreground">{chat.name}</Text>
                                        <Text className="text-xs text-muted-foreground">{chat.time}</Text>
                                    </View>
                                    <Text className="text-sm text-muted-foreground" numberOfLines={1}>
                                        {chat.lastMessage}
                                    </Text>
                                </View>

                                {chat.unread > 0 && (
                                    <View className="w-6 h-6 bg-accent rounded-full items-center justify-center">
                                        <Text className="text-xs font-bold text-white">{chat.unread}</Text>
                                    </View>
                                )}
                            </Card>
                        </TouchableOpacity>
                    ))}
                </View>

                {/* Safety Banner */}
                <View className="px-6 pb-6">
                    <Card className="p-4 shadow-sm rounded-3xl bg-secondary/30 flex-row items-start gap-3">
                        <Flag size={20} className="text-primary mt-0.5" color="#14b8a6" />
                        <View className="flex-1">
                            <Text className="font-semibold mb-1 text-foreground text-sm">Safe Community Guidelines</Text>
                            <Text className="text-muted-foreground text-xs">
                                Be respectful, kind, and supportive. Report any inappropriate behavior.
                            </Text>
                        </View>
                    </Card>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}
