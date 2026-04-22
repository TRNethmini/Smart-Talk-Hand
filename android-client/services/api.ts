import { Platform } from 'react-native';

import { API_BASE_URL } from '../constants/config';

type Listener = (data: any) => void;

class HttpInferenceService {
    private listeners: Listener[] = [];
    private errorListeners: Listener[] = [];
    private token: string | null = null;
    
    setToken(t: string | null) {
        this.token = t;
    }

    private get headers() {
        const h: Record<string, string> = { 'Content-Type': 'application/json' };
        if (this.token) {
            h['Authorization'] = `Bearer ${this.token}`;
        }
        return h;
    }

    async get(path: string) {
        const resp = await fetch(`${API_BASE_URL}${path}`, { headers: this.headers });
        if (!resp.ok) throw new Error(`HTTP Error ${resp.status}`);
        return resp.json();
    }

    async post(path: string, body: any) {
        const resp = await fetch(`${API_BASE_URL}${path}`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(body)
        });
        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP Error ${resp.status}`);
        }
        return resp.json();
    }

    async fetchModels(): Promise<string[]> {
        try {
            console.log(`Fetching models from ${API_BASE_URL}...`);
            const json = await this.get('/api/v1/models');
            return json.models || [];
        } catch (e) {
            console.error("Failed to fetch models", e);
            return [];
        }
    }

    getClassVideoUrl(modelName: string, className: string): string {
        return `${API_BASE_URL}/api/v1/models/${modelName}/classes/${encodeURIComponent(className)}/video`;
    }

    async getRagFeedback(expected: string, predicted: string): Promise<string> {
        try {
            const json = await this.post(`/api/v1/rag/feedback`, { expected, predicted });
            return json.feedback || "Feedback failed to generate.";
        } catch (e) {
            console.error("Failed to fetch RAG feedback", e);
            return "Unable to connect to AI Tutor.";
        }
    }

    async fetchClasses(modelName: string): Promise<string[]> {
        try {
            const json = await this.get(`/api/v1/models/${modelName}/classes`);
            return json.classes || [];
        } catch (e) {
            console.error(`Failed to fetch classes for ${modelName}`, e);
            return [];
        }
    }

    async sendSequence(modelName: string, frames: string[], mirror: boolean = false) {
        try {
            const json = await this.post(`/api/v1/models/${modelName}/webcam-sequence`, { frames, mirror });
            const top0 = Array.isArray(json.topk) && json.topk.length ? json.topk[0] : null;
            this.listeners.forEach(l => l({
                status: 'prediction',
                label: json.predicted_label,
                confidence: top0 ? top0.prob : 0,
                frames: frames.length,
                topk: json.topk
            }));
        } catch (e: any) {
            console.error('Failed to send sequence', e);
            this.errorListeners.forEach(l => l(e));
            this.listeners.forEach(l => l({ status: 'error', message: e.message }));
        }
    }

    addMessageListener(listener: Listener) {
        this.listeners.push(listener);
    }

    removeMessageListener(listener: Listener) {
        this.listeners = this.listeners.filter(l => l !== listener);
    }

    addErrorListener(listener: Listener) {
        this.errorListeners.push(listener);
    }

    removeErrorListener(listener: Listener) {
        this.errorListeners = this.errorListeners.filter(l => l !== listener);
    }

    connect() {}
    disconnect() {}
}

export const apiService = new HttpInferenceService();
