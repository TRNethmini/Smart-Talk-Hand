import { useState, useEffect } from "react";
import { View, Text, ScrollView, TouchableOpacity } from "react-native";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { useAuth } from "../../context/AuthContext";
import { Card } from "../../components/ui/card";
import { Progress } from "../../components/ui/progress";
import {
  Hand,
  Camera,
  MessageCircle,
  Settings as SettingsIcon,
  BookOpen,
  Star,
  TrendingUp,
  Award
} from "lucide-react-native";
import { apiService } from "../../services/api";

export default function Dashboard() {
  const router = useRouter();
  const { user } = useAuth();
  const [models, setModels] = useState<string[]>([]);

  useEffect(() => {
    async function loadModels() {
      const fetchedModels = await apiService.fetchModels();
      setModels(fetchedModels);
    }
    loadModels();
  }, []);

  return (
    <SafeAreaView className="flex-1 bg-background" edges={['top']}>
      {/* Header */}
      <View className="bg-background/80 blur-md border-b border-border z-10 px-6 py-4 flex-row items-center justify-between">
        <View className="flex-row items-center gap-3">
          <View className="bg-primary/10 p-2 rounded-xl">
            <Hand size={24} className="text-primary" color="#14b8a6" />
          </View>
          <View>
            <Text className="text-xl font-bold text-foreground">Smart TalkHand</Text>
            <Text className="text-xs text-muted-foreground">Keep learning!</Text>
          </View>
        </View>
        <TouchableOpacity
          onPress={() => router.push("/(tabs)/settings")}
          className="p-2"
        >
          <SettingsIcon size={20} className="text-foreground" color="#334155" />
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={{ paddingBottom: 120 }}>

        {/* Main Content */}
        <View className="px-6 py-8 gap-10">
          {/* Welcome Card */}
          <Card className="p-6 shadow-sm rounded-3xl bg-primary overflow-hidden">
            {/* Gradient simulation with View absolute or just bg-primary for now */}
            <View className="flex-row items-center justify-between">
              <View>
                <Text className="text-2xl font-bold mb-2 text-primary-foreground">Welcome back, {user?.name?.split(' ')[0] || "Learner"}!</Text>
                <Text className="text-primary-foreground/90">Ready to learn today?</Text>
              </View>
              <Award size={48} className="opacity-80 text-primary-foreground" color="white" />
            </View>
          </Card>

          {/* Quick Actions */}
          <View className="flex-row gap-5">
            <TouchableOpacity
              className="flex-1"
              onPress={() => router.push("/(tabs)/chat")}
            >
              <Card className="p-6 shadow-sm rounded-3xl items-center text-center gap-4 bg-card">
                <View className="bg-accent/10 p-4 rounded-2xl">
                  <MessageCircle size={32} className="text-accent" color="#f97316" />
                </View>
                <View className="items-center">
                  <Text className="font-semibold text-foreground">Chat Directory</Text>
                  <Text className="text-xs text-muted-foreground">Community Hub</Text>
                </View>
              </Card>
            </TouchableOpacity>
          </View>

          {/* Highlighted Alphabet Module */}
          <View className="gap-6">
            <Text className="text-lg font-semibold px-1 text-foreground">Featured Module</Text>
            {models.includes("ssl_alphabet") ? (
              <TouchableOpacity
                onPress={() => router.push(`/model-classes?model=ssl_alphabet`)}
              >
                <Card className="p-6 shadow-md rounded-3xl bg-primary border border-primary-foreground/20 flex-row items-center gap-5">
                  <View className="p-4 rounded-2xl bg-white/20">
                     <BookOpen size={32} color="white" />
                  </View>
                  <View className="flex-1">
                    <Text className="text-xl font-bold mb-1 text-primary-foreground">
                        ALPHABET
                    </Text>
                    <Text className="text-sm text-primary-foreground/90 leading-tight">
                        AI-powered RAG Tutor inside! Master your letters with instant, personalized feedback.
                    </Text>
                  </View>
                </Card>
              </TouchableOpacity>
            ) : null}
          </View>

          {/* Learning Categories */}
          <View className="gap-6">
            <Text className="text-lg font-semibold px-1 text-foreground">More Practice Models</Text>
            {models.length === 0 ? (
                <Text className="text-muted-foreground">Loading models from API...</Text>
            ) : models.filter(m => m !== "ssl_alphabet").map((modelName) => (
              <TouchableOpacity
                key={modelName}
                onPress={() => router.push(`/model-classes?model=${encodeURIComponent(modelName)}`)}
              >
                <Card className="p-5 shadow-sm rounded-2xl bg-card flex-row items-center gap-5">
                  <View className="p-3 rounded-xl bg-primary/10">
                     <BookOpen size={24} color="#14b8a6" />
                  </View>
                  <View className="flex-1">
                    <Text className="font-semibold mb-2 text-foreground">
                        {modelName.replace("ssl_", "").toUpperCase()}
                    </Text>
                    <Text className="text-xs text-muted-foreground mt-1">
                      Tap to view all signs
                    </Text>
                  </View>
                </Card>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
