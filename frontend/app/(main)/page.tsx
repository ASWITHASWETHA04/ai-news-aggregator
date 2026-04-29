"use client";

/**
 * Home page — personalized news feed + trending section.
 */

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/context/AuthContext";
import { newsAPI } from "@/lib/api";
import { Article, CATEGORIES } from "@/lib/types";
import NewsCard from "@/components/NewsCard";
import { NewsCardSkeletonGrid, CompactCardSkeleton } from "@/components/LoadingSkeleton";
import Link from "next/link";
import toast from "react-hot-toast";
import { FiRefreshCw, FiTrendingUp, FiZap } from "react-icons/fi";

export default function HomePage() {
  const { user } = useAuth();
  const [articles, setArticles] = useState<Article[]>([]);
  const [trending, setTrending] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [trendingLoading, setTrendingLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeCategory, setActiveCategory] = useState("all");

  const fetchFeed = useCallback(async () => {
    if (!user) return;
    try {
      setLoading(true);
      const res = await newsAPI.getFeed(30);
      setArticles(res.data.articles || []);
    } catch (err: any) {
      if (err.response?.status !== 401) {
        toast.error("Failed to load news feed.");
      }
    } finally {
      setLoading(false);
    }
  }, [user]);

  const fetchTrending = useCallback(async () => {
    try {
      setTrendingLoading(true);
      const res = await newsAPI.getTrending(6);
      setTrending(res.data.articles || []);
    } catch {
      // Silently fail for trending
    } finally {
      setTrendingLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFeed();
    fetchTrending();
  }, [fetchFeed, fetchTrending]);

  const handleRefresh = async () => {
    if (!user) return;
    setRefreshing(true);
    try {
      await newsAPI.refresh();
      await fetchFeed();
      toast.success("News feed refreshed!");
    } catch {
      toast.error("Failed to refresh.");
    } finally {
      setRefreshing(false);
    }
  };

  // Filter articles by active category
  const filteredArticles =
    activeCategory === "all"
      ? articles
      : articles.filter((a) => a.category === activeCategory);

  // Get user's preference categories for filter tabs
  const userCategories = user?.preferences || [];
  const filterTabs = [
    { id: "all", label: "All" },
    ...CATEGORIES.filter((c) => userCategories.includes(c.id)).map((c) => ({
      id: c.id,
      label: c.label,
    })),
  ];

  if (!user) {
    return (
      <div className="text-center py-20 animate-fade-in">
        <div className="text-6xl mb-6">📰</div>
        <h1 className="text-4xl font-bold text-slate-900 dark:text-slate-100 mb-4">
          AI-Powered News Aggregator
        </h1>
        <p className="text-xl text-slate-500 dark:text-slate-400 mb-8 max-w-2xl mx-auto">
          Get personalized news, AI summaries, and intelligent answers to your questions
          — all powered by RAG technology.
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/signup" className="btn-primary text-lg px-8 py-3">
            Get Started Free
          </Link>
          <Link href="/login" className="btn-secondary text-lg px-8 py-3">
            Login
          </Link>
        </div>

        {/* Feature highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16 text-left">
          {[
            { icon: "🤖", title: "AI Chatbot", desc: "Ask questions about today's news and get intelligent answers powered by RAG." },
            { icon: "🎯", title: "Personalized Feed", desc: "News tailored to your interests — technology, sports, business, and more." },
            { icon: "⚡", title: "Real-time Updates", desc: "Fresh news from multiple sources, aggregated and organized for you." },
          ].map((f) => (
            <div key={f.title} className="card p-6">
              <div className="text-3xl mb-3">{f.icon}</div>
              <h3 className="font-bold text-lg mb-2">{f.title}</h3>
              <p className="text-slate-500 dark:text-slate-400 text-sm">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
            Good day, {user.name.split(" ")[0]}! 👋
          </h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">
            Your personalized news feed
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="btn-secondary flex items-center gap-2 text-sm"
        >
          <FiRefreshCw className={refreshing ? "animate-spin" : ""} />
          {refreshing ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {/* Trending Section */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <FiTrendingUp className="text-orange-500 text-xl" />
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">Trending Now</h2>
        </div>
        {trendingLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => <CompactCardSkeleton key={i} />)}
          </div>
        ) : trending.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {trending.slice(0, 3).map((article, i) => (
              <NewsCard key={i} article={article} variant="compact" />
            ))}
          </div>
        ) : (
          <p className="text-slate-400 text-sm">No trending articles yet.</p>
        )}
      </section>

      {/* Personalized Feed */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <FiZap className="text-blue-500 text-xl" />
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">Your Feed</h2>
        </div>

        {/* Category filter tabs */}
        {filterTabs.length > 1 && (
          <div className="flex gap-2 overflow-x-auto pb-2 mb-6 scrollbar-hide">
            {filterTabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveCategory(tab.id)}
                className={`px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
                  activeCategory === tab.id
                    ? "bg-blue-600 text-white"
                    : "bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        )}

        {loading ? (
          <NewsCardSkeletonGrid count={6} />
        ) : filteredArticles.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredArticles.map((article, i) => (
              <NewsCard key={i} article={article} />
            ))}
          </div>
        ) : (
          <div className="text-center py-16 card">
            <div className="text-4xl mb-4">📭</div>
            <p className="text-slate-500 dark:text-slate-400 mb-4">
              No articles found. Try refreshing or updating your preferences.
            </p>
            <div className="flex gap-3 justify-center">
              <button onClick={handleRefresh} className="btn-primary text-sm">
                Refresh Feed
              </button>
              <Link href="/preferences" className="btn-secondary text-sm">
                Update Preferences
              </Link>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
