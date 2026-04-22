import { useState } from "react";
import { View, Text, TouchableOpacity, KeyboardAvoidingView, Platform, ScrollView } from "react-native";
import { useRouter } from "expo-router";
import { useAuth } from "../context/AuthContext";
import { apiService } from "../services/api";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card } from "../components/ui/card";
import { Hand, Mail, Lock, ArrowLeft } from "lucide-react-native";
import { AntDesign } from "@expo/vector-icons";
import { SafeAreaView } from "react-native-safe-area-context";

export default function Login() {
    const router = useRouter();
    const [isSignUp, setIsSignUp] = useState(false);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const { login } = useAuth();
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async () => {
        if (!email || !password) {
            alert("Please enter both email and password.");
            return;
        }
        setIsLoading(true);
        try {
            if (isSignUp) {
                // Register
                const name = email.split('@')[0]; // Simple mock name
                await apiService.post('/api/v1/auth/register', { name, email, password });
                
                // Then auto-login
                const loginParams = new URLSearchParams();
                loginParams.append('username', email);
                loginParams.append('password', password);
                
                // We use standard fetch here because OAuth2 form consumes urlencoded
                const resp = await fetch(`${apiService.getClassVideoUrl('','').split('/api')[0]}/api/v1/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: loginParams.toString()
                });
                if (!resp.ok) throw new Error("Auto-login failed");
                const data = await resp.json();
                
                // Fetch profile
                apiService.setToken(data.access_token);
                const userResp = await apiService.get('/api/v1/auth/me');
                await login(data.access_token, userResp);
                
            } else {
                // Login Flow
                const params = new URLSearchParams();
                params.append('username', email);
                params.append('password', password);
                
                const resp = await fetch(`${apiService.getClassVideoUrl('','').split('/api')[0]}/api/v1/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: params.toString()
                });
                
                if (!resp.ok) {
                    const err = await resp.json().catch(() => ({}));
                    throw new Error(err.detail || "Login failed");
                }
                const data = await resp.json();
                
                // Fetch user data
                apiService.setToken(data.access_token);
                const userResp = await apiService.get('/api/v1/auth/me');
                
                await login(data.access_token, userResp);
            }
            router.replace("/(tabs)");
        } catch (e: any) {
            alert(e.message || "Failed to authenticate");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <SafeAreaView className="flex-1 bg-background" edges={['top', 'left', 'right']}>
            <KeyboardAvoidingView
                behavior={Platform.OS === "ios" ? "padding" : "height"}
                className="flex-1"
            >
                <ScrollView contentContainerStyle={{ flexGrow: 1 }}>
                    <View className="flex-1 px-6 py-4 justify-center">
                        {/* Back Button */}
                        <TouchableOpacity
                            onPress={() => router.back()}
                            className="flex-row items-center gap-2 mb-6 absolute top-4 left-6 z-10"
                        >
                            <ArrowLeft size={20} className="text-muted-foreground" color="#64748b" />
                            <Text className="text-muted-foreground text-base">Back</Text>
                        </TouchableOpacity>

                        <View className="items-center justify-center w-full">
                            <Card className="w-full max-w-md p-6 shadow-sm rounded-3xl bg-card">
                                {/* Logo */}
                                <View className="items-center mb-6">
                                    <View className="bg-primary/10 p-4 rounded-2xl">
                                        <Hand size={48} className="text-primary" color="#14b8a6" />
                                    </View>
                                </View>

                                {/* Title */}
                                <View className="items-center mb-6 space-y-2">
                                    <Text className="text-3xl font-bold text-foreground text-center">
                                        {isSignUp ? "Create Account" : "Welcome Back"}
                                    </Text>
                                    <Text className="text-muted-foreground text-center">
                                        {isSignUp
                                            ? "Start your sign language journey"
                                            : "Continue your learning path"}
                                    </Text>
                                </View>

                                {/* Form */}
                                <View className="space-y-4 mb-6">
                                    <View className="space-y-2">
                                        <Label className="mb-1">Email</Label>
                                        <View className="relative justify-center">
                                            <View className="absolute left-3 z-10">
                                                <Mail size={20} className="text-muted-foreground" color="#9ca3af" />
                                            </View>
                                            <Input
                                                className="pl-10 h-12 rounded-xl"
                                                placeholder="your@email.com"
                                                value={email}
                                                onChangeText={setEmail}
                                                autoCapitalize="none"
                                                keyboardType="email-address"
                                            />
                                        </View>
                                    </View>

                                    <View className="space-y-2">
                                        <Label className="mb-1">Password</Label>
                                        <View className="relative justify-center">
                                            <View className="absolute left-3 z-10">
                                                <Lock size={20} className="text-muted-foreground" color="#9ca3af" />
                                            </View>
                                            <Input
                                                className="pl-10 h-12 rounded-xl"
                                                placeholder="••••••••"
                                                secureTextEntry
                                                value={password}
                                                onChangeText={setPassword}
                                            />
                                        </View>
                                    </View>

                                    <Button
                                        variant="default"
                                        size="lg"
                                        className="w-full mt-2 bg-primary"
                                        onPress={handleSubmit}
                                        disabled={isLoading}
                                    >
                                        <Text className="text-primary-foreground font-semibold">{isLoading ? (isSignUp ? "Creating..." : "Logging In...") : (isSignUp ? "Sign Up" : "Sign In")}</Text>
                                    </Button>
                                </View>

                                {/* Divider */}
                                <View className="relative mb-6 justify-center">
                                    <View className="absolute inset-0 flex-row items-center">
                                        <View className="w-full border-t border-border" />
                                    </View>
                                    <View className="relative flex-row justify-center">
                                        <Text className="bg-card px-4 text-sm text-muted-foreground">or</Text>
                                    </View>
                                </View>

                                {/* Google Sign In */}
                                <Button
                                    variant="outline"
                                    size="lg"
                                    className="w-full mb-6 flex-row gap-2 border-input"
                                >
                                    <AntDesign name="google" size={20} color="black" />
                                    <Text className="text-foreground font-medium">Continue with Google</Text>
                                </Button>

                                {/* Toggle */}
                                <View className="flex-row justify-center gap-1">
                                    <Text className="text-sm text-muted-foreground">
                                        {isSignUp ? "Already have an account?" : "Don't have an account?"}
                                    </Text>
                                    <TouchableOpacity onPress={() => setIsSignUp(!isSignUp)}>
                                        <Text className="text-sm font-medium text-primary">
                                            {isSignUp ? "Sign In" : "Sign Up"}
                                        </Text>
                                    </TouchableOpacity>
                                </View>
                            </Card>
                        </View>
                    </View>
                </ScrollView>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}
