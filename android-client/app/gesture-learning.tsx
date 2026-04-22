import { useState, useEffect, useRef } from "react";
import { StyleSheet, View, Text, TouchableOpacity, ScrollView, Image } from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { Card } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { ArrowLeft, RotateCcw, Activity, Eye, EyeOff } from "lucide-react-native";
import { Camera as VisionCamera, useCameraDevice, useCameraPermission } from 'react-native-vision-camera';
import * as FileSystem from 'expo-file-system/legacy';
import { useVideoPlayer, VideoView } from 'expo-video';
import { apiService } from "../services/api";

const TARGET_FRAME_COUNT = 30;
const CAPTURE_INTERVAL_MS = 120;

export default function GestureLearning() {
    const router = useRouter();
    const params = useLocalSearchParams();
    const modelName = (params.model as string) || '';
    const targetSign = (params.target as string) || '';

    const [feedback, setFeedback] = useState(targetSign ? `Target: ${targetSign}` : 'Hold your sign steady and press Start Capture');
    const [prediction, setPrediction] = useState<string | null>(null);
    const [capturing, setCapturing] = useState(false);
    const [frameCount, setFrameCount] = useState(0);

    const [aiFeedback, setAiFeedback] = useState<string | null>(null);
    const [isThinking, setIsThinking] = useState(false);

    const { hasPermission, requestPermission } = useCameraPermission();
    const device = useCameraDevice('front');
    const cameraRef = useRef<VisionCamera>(null);
    const captureTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
    const capturedFramesRef = useRef<string[]>([]);

    const [showVideo, setShowVideo] = useState(true);
    const [isScreenReady, setIsScreenReady] = useState(false);

    useEffect(() => {
        // Delay rendering secondary SurfaceViews (Video player) until the screen transition finishes
        // This prevents the Camera SurfaceView from glitching and overlapping the video on first mount
        const timer = setTimeout(() => setIsScreenReady(true), 500);
        return () => clearTimeout(timer);
    }, []);

    const videoSource = targetSign ? apiService.getClassVideoUrl(modelName, targetSign) : '';
    const player = useVideoPlayer(videoSource, player => {
        player.loop = true;
        player.muted = true;
        player.play();
    });

    useEffect(() => {
        if (!hasPermission) {
            requestPermission();
        }
    }, [hasPermission, requestPermission]);

    useEffect(() => {
        const listener = (data: any) => {
            if (data.status === 'prediction') {
                const label: string = data.label;
                const conf: number = data.confidence || 0;
                const confPct = (conf * 100).toFixed(0);
                setPrediction(label);

                if (!targetSign) {
                    setFeedback(`Detected: ${label} (${confPct}%)`);
                } else if (label === targetSign && conf >= 0.7) {
                    setFeedback(`✅ Great job! You correctly signed "${targetSign}" (${confPct}%)`);
                    setAiFeedback(null);
                } else if (label === targetSign) {
                    setFeedback(`Almost! Detected "${label}" but low confidence (${confPct}%). Try again.`);
                    setAiFeedback(null);
                } else {
                    setFeedback(`❌ Saw "${label}" (${confPct}%) instead of "${targetSign}".`);
                    if (modelName === "ssl_alphabet") {
                        setIsThinking(true);
                        setAiFeedback(null);
                        apiService.getRagFeedback(targetSign, label).then(msg => {
                            setAiFeedback(msg);
                            setIsThinking(false);
                        }).catch(e => {
                            setAiFeedback("Failed to load AI Tutor. Try again.");
                            setIsThinking(false);
                        });
                    }
                }
            } else if (data.status === 'error') {
                setPrediction('Error');
                setFeedback(data.message || 'Unknown error');
            }
        };
        apiService.addMessageListener(listener);
        return () => { apiService.removeMessageListener(listener); };
    }, [targetSign]);

    const startCapture = () => {
        if (capturing || !cameraRef.current) return;
        if (!modelName) {
            setFeedback('No model selected. Go back and pick a model.');
            return;
        }

        capturedFramesRef.current = [];
        setFrameCount(0);
        setCapturing(true);
        setPrediction(null);
        setFeedback('Capturing frames...');

        captureTimerRef.current = setInterval(async () => {
            try {
                if (!cameraRef.current?.takeSnapshot) return;
                const photo = await cameraRef.current.takeSnapshot({ quality: 80 });
                const path = photo.path.startsWith('file://') ? photo.path : `file://${photo.path}`;
                const base64Data = await FileSystem.readAsStringAsync(path, { encoding: 'base64' });
                const base64 = `data:image/jpeg;base64,${base64Data}`;
                capturedFramesRef.current.push(base64);
                const count = capturedFramesRef.current.length;
                setFrameCount(count);

                if (count >= TARGET_FRAME_COUNT) {
                    clearInterval(captureTimerRef.current!);
                    captureTimerRef.current = null;
                    setCapturing(false);
                    setFeedback('Sending to server...');
                    await apiService.sendSequence(modelName, capturedFramesRef.current, true);
                }
            } catch (e) {
                console.error('Capture error', e);
            }
        }, CAPTURE_INTERVAL_MS);
    };

    const resetCapture = () => {
        if (captureTimerRef.current) {
            clearInterval(captureTimerRef.current);
            captureTimerRef.current = null;
        }
        capturedFramesRef.current = [];
        setCapturing(false);
        setFrameCount(0);
        setPrediction(null);
        setAiFeedback(null);
        setIsThinking(false);
        setFeedback(targetSign ? `Target: ${targetSign}` : 'Hold your sign steady and press Start Capture');
    };

    const progress = Math.round((frameCount / TARGET_FRAME_COUNT) * 100);

    return (
        <SafeAreaView className="flex-1 bg-background" edges={['top']}>
            {/* Header */}
            <View className="bg-background/80 border-b border-border z-10 px-6 py-4 flex-row items-center justify-between">
                <TouchableOpacity onPress={() => router.back()} className="flex-row items-center gap-2">
                    <ArrowLeft size={20} color="#64748b" />
                    <Text className="text-muted-foreground">Back</Text>
                </TouchableOpacity>
                <Text className="text-lg font-semibold text-foreground">
                    {targetSign ? `"${targetSign}"` : 'Gesture Practice'}
                </Text>
                <View className="w-16 items-end">
                    {targetSign && (
                        <TouchableOpacity onPress={() => setShowVideo(!showVideo)}>
                            {showVideo ? <EyeOff size={24} color="#64748b" /> : <Eye size={24} color="#64748b" />}
                        </TouchableOpacity>
                    )}
                </View>
            </View>

            <ScrollView contentContainerStyle={{ paddingBottom: 40 }}>
                <View className="px-6 py-6 gap-6">

                    {/* Camera + ViewShot */}
                    <Card className="overflow-hidden rounded-3xl bg-black h-80 justify-center items-center relative">
                        {!hasPermission ? (
                            <View className="items-center justify-center flex-1">
                                <Text className="text-white text-center mb-2">Camera permission required</Text>
                                <Button onPress={requestPermission} variant="outline">
                                    <Text>Grant Permission</Text>
                                </Button>
                            </View>
                        ) : !device ? (
                            <Text className="text-white">Loading camera...</Text>
                        ) : (
                            <VisionCamera
                                ref={cameraRef}
                                style={StyleSheet.absoluteFillObject}
                                device={device}
                                isActive={true}
                                photo={true}
                            />
                        )}

                        {/* Feedback Banner */}
                        <View className="absolute top-4 left-4 right-4">
                            <Card className="p-3 bg-card/95 justify-center items-center rounded-xl shadow-md border border-border">
                                <Text className="text-sm text-center font-medium text-foreground">
                                    {feedback}
                                </Text>
                            </Card>
                        </View>
                    </Card>

                    {/* Reference Video Player */}
                    {targetSign && showVideo && (
                        <Card className="overflow-hidden rounded-3xl bg-black h-48 justify-center items-center relative">
                            {isScreenReady ? (
                                <VideoView
                                    player={player}
                                    style={StyleSheet.absoluteFillObject}
                                    allowsFullscreen
                                    allowsPictureInPicture
                                />
                            ) : (
                                <Text className="text-white text-xs">Loading reference...</Text>
                            )}
                            <View className="absolute bottom-2 left-2 bg-black/60 px-2 py-1 rounded-md">
                                <Text className="text-xs text-white">Reference Video</Text>
                            </View>
                        </Card>
                    )}

                    {/* Progress Bar */}
                    {capturing && (
                        <View className="gap-1">
                            <Text className="text-xs text-muted-foreground text-center">
                                Capturing {frameCount}/{TARGET_FRAME_COUNT} frames
                            </Text>
                            <View className="h-2 bg-muted rounded-full overflow-hidden">
                                <View
                                    className="h-full bg-primary rounded-full"
                                    style={{ width: `${progress}%` }}
                                />
                            </View>
                        </View>
                    )}

                    {/* Captured Frames Debug Viewer */}
                    {frameCount > 0 && (
                        <View className="gap-2">
                            <Text className="text-xs text-muted-foreground">Captured Frames ({frameCount})</Text>
                            <ScrollView horizontal showsHorizontalScrollIndicator={false} className="flex-row gap-2">
                                {capturedFramesRef.current.map((frameUri, i) => (
                                    <View key={i} className="rounded-md overflow-hidden border border-border">
                                        <Image
                                            source={{ uri: frameUri }}
                                            style={{ width: 60, height: 80 }}
                                            resizeMode="cover"
                                        />
                                        <View className="absolute bottom-0 right-0 bg-black/50 px-1 rounded-tl-sm">
                                            <Text className="text-[8px] text-white">{i + 1}</Text>
                                        </View>
                                    </View>
                                ))}
                            </ScrollView>
                        </View>
                    )}

                    {/* Prediction Result */}
                    {prediction && (
                        <Card className="p-6 rounded-3xl bg-card items-center">
                            <Text className="text-lg font-semibold text-foreground mb-2">Result</Text>
                            <Text className={`text-3xl font-bold text-center ${
                                prediction === targetSign ? 'text-primary' : 'text-destructive'
                            }`}>
                                {prediction}
                            </Text>
                        </Card>
                    )}

                    {/* AI Tutor Feedback */}
                    {(isThinking || aiFeedback) && (
                        <Card className="rounded-3xl overflow-hidden border border-primary/30 bg-card shadow-md">
                            {/* Header bar */}
                            <View className="bg-primary px-5 py-3 flex-row items-center gap-3">
                                <View className="bg-white/20 p-1.5 rounded-lg">
                                    <Activity size={16} color="white" />
                                </View>
                                <View className="flex-1">
                                    <Text className="text-sm font-bold text-primary-foreground">AI Tutor</Text>
                                    <Text className="text-xs text-primary-foreground/70">Powered by Gemma3 · RAG</Text>
                                </View>
                                {isThinking && (
                                    <View className="bg-white/20 px-2.5 py-1 rounded-full">
                                        <Text className="text-xs text-white font-medium">Analysing...</Text>
                                    </View>
                                )}
                            </View>

                            {/* Body */}
                            <View className="p-5">
                                {isThinking ? (
                                    <View className="gap-2">
                                        <Text className="text-sm text-muted-foreground italic">
                                            🧠 Searching textbook for "{targetSign}" gesture details...
                                        </Text>
                                        <View className="h-1.5 bg-muted rounded-full overflow-hidden mt-1">
                                            <View className="h-full w-1/3 bg-primary rounded-full" />
                                        </View>
                                    </View>
                                ) : (
                                    <View className="gap-3">
                                        <View className="flex-row items-start gap-2">
                                            <Text className="text-primary text-base mt-0.5">💡</Text>
                                            <Text className="text-foreground text-sm leading-6 flex-1">{aiFeedback}</Text>
                                        </View>
                                        <View className="bg-secondary/50 rounded-xl px-4 py-2.5 mt-1">
                                            <Text className="text-xs text-muted-foreground text-center">
                                                Target: <Text className="font-bold text-primary">{targetSign}</Text>  ·  Detected: <Text className="font-bold text-destructive">{prediction}</Text>
                                            </Text>
                                        </View>
                                    </View>
                                )}
                            </View>
                        </Card>
                    )}

                    {/* Model/Sign Info */}
                    {modelName ? (
                        <Card className="p-4 rounded-2xl bg-card">
                            <Text className="text-xs text-muted-foreground">
                                Model: <Text className="text-foreground font-medium">{modelName.replace('ssl_', '').toUpperCase()}</Text>
                                {targetSign ? '  ·  Target: ' : ''}
                                {targetSign ? <Text className="text-primary font-medium">{targetSign}</Text> : null}
                            </Text>
                        </Card>
                    ) : null}

                    {/* Controls */}
                    <View className="flex-row gap-4">
                        <Button
                            variant="outline"
                            size="lg"
                            className="flex-1 bg-background"
                            onPress={resetCapture}
                        >
                            <RotateCcw size={18} color="#0f172a" />
                            <Text className="text-foreground ml-2">Reset</Text>
                        </Button>
                        <Button
                            variant="default"
                            size="lg"
                            className="flex-1 bg-primary"
                            onPress={startCapture}
                            disabled={capturing}
                        >
                            <Activity size={18} color="white" />
                            <Text className="text-primary-foreground ml-2">
                                {capturing ? `${frameCount}/${TARGET_FRAME_COUNT}` : 'Start Capture'}
                            </Text>
                        </Button>
                    </View>
                </View>
            </ScrollView>
        </SafeAreaView>
    );
}
