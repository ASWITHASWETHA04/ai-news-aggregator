"use client";

/**
 * Search page — keyword-based article search.
 */

import { useState, useCallback } from "react";
import ProtectedRoute from "@/components/ProtectedRoute";
import { newsAPI } from "@/lib/api";
import { Article } from "@/lib/types";
import NewsCard from "@/components/NewsCard";
import { NewsCardSkeletonGrid } from "@/components/LoadingSkeleton";
import { FiSearch, FiX } from "react-icons/fi";
import toast from "react-hot-toast";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = useCallback(async (q?: string) => {
    const searchQuery = q ?? query;
    if (!searchQuery.trim() || searchQuery.trim().length < 2) {
      toast.error("Please enter at least 2 characters.");
      return;
    }

    setLoading(true);
    setSearched(true);
    try {
      const res = await newsAPI.search(searchQuery.trim());
      setResults(res.data.articles || []);
    } catch (err: any) {
      toast.error("Search failed. Please try again.");
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [query]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSearch();
  };

  const clearSearch = () => {
    setQuery("");
    setResults([]);
    setSearched(false);
  };

  const POPULAR_SEARCHES = [
    "artificial intelligence", "climate change", "stock market",
    "space exploration", "electric vehicles", "cryptocurrency",
  ];

  return (
    <ProtectedRoute>
      <div className="animate-fade-in">
        <div className="max-w-2xl mx-auto mb-8">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-6">
            Search News
          </h1>

          {/* Search input */}
          <div className="relative">
            <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 text-lg" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Search for news topics, keywords..."
              className="input-field pl-11 pr-12 py-3 text-base"
              autoFocus
            />
            {query && (
              <button
                onClick={clearSearch}
                className="absolute right-14 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                <FiX />
              </button>
            )}
            <button
              onClick={() => handleSearch()}
              disabled={loading}
              className="absolute right-3 top-1/2 -translate-y-1/2 btn-primary py-1.5 px-3 text-sm"
            >
              {loading ? "..." : "Search"}
            </button>
          </div>

          {/* Popular searches */}
          {!searched && (
            <div className="mt-4">
              <p className="text-xs text-slate-400 mb-2">Popular searches:</p>
              <div className="flex flex-wrap gap-2">
                {POPULAR_SEARCHES.map((s) => (
                  <button
                    key={s}
                    onClick={() => { setQuery(s); handleSearch(s); }}
                    className="text-xs px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Results */}
        {loading ? (
          <NewsCardSkeletonGrid count={6} />
        ) : searched ? (
          results.length > 0 ? (
            <div>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">
                Found {results.length} result{results.length !== 1 ? "s" : ""} for &quot;{query}&quot;
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {results.map((article, i) => (
                  <NewsCard key={i} article={article} />
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-16">
              <div className="text-4xl mb-4">🔍</div>
              <p className="text-slate-500 dark:text-slate-400 text-lg mb-2">
                No results found for &quot;{query}&quot;
              </p>
              <p className="text-slate-400 text-sm">
                Try different keywords or refresh your news feed first.
              </p>
            </div>
          )
        ) : null}
      </div>
    </ProtectedRoute>
  );
}
