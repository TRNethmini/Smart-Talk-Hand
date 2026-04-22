import { useState, useEffect } from "react";
import { View, Text, ScrollView, TouchableOpacity } from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { Card } from "../components/ui/card";
import { ArrowLeft, BookOpen } from "lucide-react-native";
import { apiService } from "../services/api";

export default function ModelClasses() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const modelName = params.model as string;

  const [classes, setClasses] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchModelClasses() {
      if (!modelName) return;
      const data = await apiService.fetchClasses(modelName);
      setClasses(data);
      setLoading(false);
    }
    fetchModelClasses();
  }, [modelName]);

  return (
    <SafeAreaView className="flex-1 bg-background" edges={['top']}>
      <View className="bg-background/80 blur-md border-b border-border z-10 px-6 py-4 flex-row items-center justify-between">
        <TouchableOpacity
            onPress={() => router.back()}
            className="flex-row items-center gap-2"
        >
            <ArrowLeft size={20} className="text-muted-foreground" color="#64748b" />
            <Text className="text-muted-foreground">Back</Text>
        </TouchableOpacity>
        <Text className="text-lg font-semibold text-foreground">Target Sign Selection</Text>
        <View className="w-16" />
      </View>

      <ScrollView contentContainerStyle={{ paddingBottom: 120 }}>
        <View className="px-6 py-8 gap-6">
          <Text className="text-xl font-semibold px-1 text-foreground">
              {modelName ? modelName.replace("ssl_", "").toUpperCase() + " Signs" : "Model Signs"}
          </Text>

          {loading ? (
             <Text className="text-muted-foreground">Loading classes from model API...</Text>
          ) : classes.length === 0 ? (
             <Text className="text-muted-foreground">No classes found.</Text>
          ) : (
            <View className="flex-row flex-wrap gap-4">
              {classes.map((cls) => (
                <TouchableOpacity
                  key={cls}
                  className="w-[47%]"
                  onPress={() => router.push(`/lesson?model=${encodeURIComponent(modelName)}&target=${encodeURIComponent(cls)}`)}
                >
                  <Card className="p-5 shadow-sm rounded-2xl bg-card items-center gap-3">
                    <View className="p-3 rounded-full bg-primary/10">
                       <BookOpen size={24} color="#14b8a6" />
                    </View>
                    <Text className="font-semibold text-center text-foreground">{cls}</Text>
                  </Card>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
