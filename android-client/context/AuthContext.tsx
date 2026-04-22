import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiService } from '../services/api';

type UserSession = {
    id: string;
    email: string;
    name: string;
    initials: string;
};

type AuthContextType = {
    user: UserSession | null;
    isLoading: boolean;
    login: (token: string, user: UserSession) => Promise<void>;
    logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<UserSession | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        loadSession();
    }, []);

    const loadSession = async () => {
        try {
            const token = await AsyncStorage.getItem('jwt_token');
            const userData = await AsyncStorage.getItem('user_data');
            
            if (token && userData) {
                apiService.setToken(token);
                setUser(JSON.parse(userData));
            }
        } catch (e) {
            console.error('Failed to load session', e);
        } finally {
            setIsLoading(false);
        }
    };

    const login = async (token: string, sessionUser: UserSession) => {
        try {
            await AsyncStorage.setItem('jwt_token', token);
            await AsyncStorage.setItem('user_data', JSON.stringify(sessionUser));
            apiService.setToken(token);
            setUser(sessionUser);
        } catch (e) {
            console.error('Failed to save session', e);
        }
    };

    const logout = async () => {
        try {
            await AsyncStorage.removeItem('jwt_token');
            await AsyncStorage.removeItem('user_data');
            apiService.setToken(null);
            setUser(null);
        } catch (e) {
            console.error('Failed to clear session', e);
        }
    };

    return (
        <AuthContext.Provider value={{ user, isLoading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
