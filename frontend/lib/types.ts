/**
 * Shared TypeScript types for the application.
 */

export interface Article {
  title: string;
  description: string;
  content: string;
  url: string;
  image: string;
  source: string;
  category: string;
  published_at: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  timestamp?: Date;
}

export const CATEGORIES = [
  { id: "technology", label: "Technology", emoji: "💻" },
  { id: "ai", label: "Artificial Intelligence", emoji: "🤖" },
  { id: "sports", label: "Sports", emoji: "⚽" },
  { id: "business", label: "Business", emoji: "💼" },
  { id: "health", label: "Health", emoji: "🏥" },
  { id: "science", label: "Science", emoji: "🔬" },
  { id: "entertainment", label: "Entertainment", emoji: "🎬" },
  { id: "politics", label: "Politics", emoji: "🏛️" },
  { id: "world", label: "World", emoji: "🌍" },
];
