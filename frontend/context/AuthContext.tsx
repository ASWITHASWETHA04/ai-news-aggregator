"use client";

/**
 * Authentication context — provides user state and auth actions
 * to the entire application.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { User, getUser, getToken, setSession, clearSession } from "@/lib/auth";
import { authAPI } from "@/lib/api";
import toast from "react-hot-toast";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Hydrate from localStorage on mount
  useEffect(() => {
    const storedUser = getUser();
    const storedToken = getToken();
    if (storedUser && storedToken) {
      setUser(storedUser);
      setToken(storedToken);
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const res = await authAPI.login({ email, password });
    const { access_token, user: userData } = res.data;
    setSession(access_token, userData);
    setUser(userData);
    setToken(access_token);
    toast.success(`Welcome back, ${userData.name}!`);
    router.push("/");
  };

  const signup = async (name: string, email: string, password: string) => {
    const res = await authAPI.signup({ name, email, password });
    const { access_token, user: userData } = res.data;
    setSession(access_token, userData);
    setUser(userData);
    setToken(access_token);
    toast.success(`Welcome, ${userData.name}! Let's set up your preferences.`);
    router.push("/preferences");
  };

  const logout = () => {
    clearSession();
    setUser(null);
    setToken(null);
    toast.success("Logged out successfully.");
    router.push("/login");
  };

  const updateUser = (updates: Partial<User>) => {
    if (!user) return;
    const updated = { ...user, ...updates };
    setUser(updated);
    localStorage.setItem("user", JSON.stringify(updated));
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, signup, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
