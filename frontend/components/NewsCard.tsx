"use client";

import Image from "next/image";
import Link from "next/link";
import { Article } from "@/lib/types";
import { formatDistanceToNow } from "date-fns";
import { FiExternalLink, FiClock, FiTag } from "react-icons/fi";

interface NewsCardProps {
  article: Article;
  variant?: "default" | "compact" | "featured";
}

const CATEGORY_COLORS: Record<string, string> = {
  technology: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  ai: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  sports: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  business: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  health: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  science: "bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400",
  entertainment: "bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400",
  politics: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
  world: "bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400",
};

function formatDate(dateStr: string): string {
  if (!dateStr) return "";
  try {
    return formatDistanceToNow(new Date(dateStr), { addSuffix: true });
  } catch {
    return dateStr;
  }
}

export default function NewsCard({ article, variant = "default" }: NewsCardProps) {
  const categoryColor = CATEGORY_COLORS[article.category] || "bg-slate-100 text-slate-700";
  const detailUrl = `/article?url=${encodeURIComponent(article.url)}`;

  if (variant === "compact") {
    return (
      <div className="card hover:shadow-md transition-shadow p-4 flex gap-3 animate-fade-in">
        {article.image && (
          <div className="relative w-20 h-20 flex-shrink-0 rounded-lg overflow-hidden">
            <Image
              src={article.image}
              alt={article.title}
              fill
              className="object-cover"
              onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
            />
          </div>
        )}
        <div className="flex-1 min-w-0">
          <Link href={detailUrl} className="font-semibold text-sm text-slate-900 dark:text-slate-100 hover:text-blue-600 dark:hover:text-blue-400 line-clamp-2 transition-colors">
            {article.title}
          </Link>
          <div className="flex items-center gap-2 mt-1.5 text-xs text-slate-500 dark:text-slate-400">
            <span>{article.source}</span>
            {article.published_at && (
              <>
                <span>·</span>
                <span>{formatDate(article.published_at)}</span>
              </>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (variant === "featured") {
    return (
      <div className="card hover:shadow-lg transition-shadow animate-fade-in group">
        <div className="relative h-56 w-full overflow-hidden">
          {article.image ? (
            <Image
              src={article.image}
              alt={article.title}
              fill
              className="object-cover group-hover:scale-105 transition-transform duration-300"
              onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <span className="text-white text-4xl">📰</span>
            </div>
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          <div className="absolute bottom-3 left-3">
            <span className={`text-xs font-medium px-2 py-1 rounded-full ${categoryColor}`}>
              {article.category}
            </span>
          </div>
        </div>
        <div className="p-4">
          <Link href={detailUrl} className="font-bold text-lg text-slate-900 dark:text-slate-100 hover:text-blue-600 dark:hover:text-blue-400 line-clamp-2 transition-colors">
            {article.title}
          </Link>
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-2 line-clamp-2">
            {article.description}
          </p>
          <div className="flex items-center justify-between mt-3 text-xs text-slate-400">
            <span className="font-medium">{article.source}</span>
            {article.published_at && (
              <span className="flex items-center gap-1">
                <FiClock className="text-xs" />
                {formatDate(article.published_at)}
              </span>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Default card
  return (
    <div className="card hover:shadow-md transition-shadow animate-fade-in group">
      {article.image && (
        <div className="relative h-44 w-full overflow-hidden">
          <Image
            src={article.image}
            alt={article.title}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-300"
            onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }}
          />
        </div>
      )}
      <div className="p-4">
        <div className="flex items-center gap-2 mb-2">
          <span className={`text-xs font-medium px-2 py-0.5 rounded-full flex items-center gap-1 ${categoryColor}`}>
            <FiTag className="text-xs" />
            {article.category}
          </span>
          {article.source && (
            <span className="text-xs text-slate-400 dark:text-slate-500">{article.source}</span>
          )}
        </div>

        <Link href={detailUrl} className="font-semibold text-slate-900 dark:text-slate-100 hover:text-blue-600 dark:hover:text-blue-400 line-clamp-2 transition-colors leading-snug">
          {article.title}
        </Link>

        {article.description && (
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-2 line-clamp-2">
            {article.description}
          </p>
        )}

        <div className="flex items-center justify-between mt-3">
          {article.published_at && (
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <FiClock className="text-xs" />
              {formatDate(article.published_at)}
            </span>
          )}
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-blue-500 hover:text-blue-600 flex items-center gap-1 ml-auto"
            onClick={(e) => e.stopPropagation()}
          >
            Read more <FiExternalLink />
          </a>
        </div>
      </div>
    </div>
  );
}
