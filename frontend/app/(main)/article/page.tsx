"use client";

/**
 * Article detail page — full article view.
 */

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import ProtectedRoute from "@/components/ProtectedRoute";
import { newsAPI } from "@/lib/api";
import { Article } from "@/lib/types";
import Image from "next/image";
import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import { FiArrowLeft, FiExternalLink, FiClock, FiTag, FiShare2 } from "react-icons/fi";
import toast from "react-hot-toast";
import { PageLoader } from "@/components/LoadingSkeleton";

function ArticleContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const url = searchParams.get("url");

  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!url) {
      setError("No article URL provided.");
      setLoading(false);
      return;
    }

    const fetchArticle = async () => {
      try {
        const res = await newsAPI.getArticle(url);
        setArticle(res.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Article not found.");
      } finally {
        setLoading(false);
      }
    };

    fetchArticle();
  }, [url]);

  const handleShare = async () => {
    if (navigator.share && article) {
      try {
        await navigator.share({ title: article.title, url: article.url });
      } catch {
        // User cancelled
      }
    } else {
      navigator.clipboard.writeText(article?.url || "");
      toast.success("Link copied to clipboard!");
    }
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="max-w-3xl mx-auto animate-pulse space-y-4">
          <div className="skeleton h-8 w-24 rounded-lg" />
          <div className="skeleton h-64 w-full rounded-xl" />
          <div className="skeleton h-8 w-3/4" />
          <div className="skeleton h-6 w-1/2" />
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => <div key={i} className="skeleton h-4 w-full" />)}
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  if (error || !article) {
    return (
      <ProtectedRoute>
        <div className="text-center py-16">
          <div className="text-4xl mb-4">😕</div>
          <p className="text-slate-500 dark:text-slate-400 text-lg mb-4">{error || "Article not found."}</p>
          <button onClick={() => router.back()} className="btn-primary">
            Go Back
          </button>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="max-w-3xl mx-auto animate-fade-in">
        {/* Back button */}
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 mb-6 transition-colors"
        >
          <FiArrowLeft />
          Back
        </button>

        {/* Hero image */}
        {article.image && (
          <div className="relative h-64 sm:h-80 w-full rounded-2xl overflow-hidden mb-6">
            <Image
              src={article.image}
              alt={article.title}
              fill
              className="object-cover"
              priority
            />
          </div>
        )}

        {/* Meta */}
        <div className="flex flex-wrap items-center gap-3 mb-4">
          {article.category && (
            <span className="flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
              <FiTag className="text-xs" />
              {article.category}
            </span>
          )}
          {article.source && (
            <span className="text-sm font-semibold text-slate-600 dark:text-slate-300">
              {article.source}
            </span>
          )}
          {article.published_at && (
            <span className="flex items-center gap-1 text-xs text-slate-400">
              <FiClock className="text-xs" />
              {formatDistanceToNow(new Date(article.published_at), { addSuffix: true })}
            </span>
          )}
        </div>

        {/* Title */}
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-slate-100 leading-tight mb-4">
          {article.title}
        </h1>

        {/* Description */}
        {article.description && (
          <p className="text-lg text-slate-600 dark:text-slate-300 leading-relaxed mb-6 border-l-4 border-blue-500 pl-4">
            {article.description}
          </p>
        )}

        {/* Content */}
        {article.content && (
          <div className="prose prose-slate dark:prose-invert max-w-none mb-8">
            <p className="text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-line">
              {article.content.replace(/\[\+\d+ chars\]$/, "")}
            </p>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3 pt-6 border-t border-slate-200 dark:border-slate-700">
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary flex items-center gap-2"
          >
            <FiExternalLink />
            Read Full Article
          </a>
          <button
            onClick={handleShare}
            className="btn-secondary flex items-center gap-2"
          >
            <FiShare2 />
            Share
          </button>
          <Link href="/chat" className="btn-secondary flex items-center gap-2 ml-auto">
            Ask AI about this
          </Link>
        </div>
      </div>
    </ProtectedRoute>
  );
}

export default function ArticlePage() {
  return (
    <Suspense fallback={<PageLoader />}>
      <ArticleContent />
    </Suspense>
  );
}
