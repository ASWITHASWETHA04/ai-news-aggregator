"use client";

/**
 * Preferences page — users select their news categories.
 */

import { useState, useEffect } from "react";
import ProtectedRoute from "@/components/ProtectedRoute";
import { useAuth } from "@/context/AuthContext";
import { preferencesAPI } from "@/lib/api";
import { CATEGORIES } from "@/lib/types";
import toast from "react-hot-toast";
import { FiCheck, FiSave } from "react-icons/fi";
import Link from "next/link";

export default function PreferencesPage() {
  const { user, updateUser } = useAuth();
  const [selected, setSelected] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadPreferences = async () => {
      try {
        const res = await preferencesAPI.get();
        setSelected(res.data.categories || []);
      } catch {
        // Fall back to user context
        setSelected(user?.preferences || []);
      } finally {
        setLoading(false);
      }
    };
    loadPreferences();
  }, [user]);

  const toggleCategory = (id: string) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );
  };

  const handleSave = async () => {
    if (selected.length === 0) {
      toast.error("Please select at least one category.");
      return;
    }
    setSaving(true);
    try {
      await preferencesAPI.update(selected);
      updateUser({ preferences: selected });
      toast.success("Preferences saved!");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to save preferences.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="max-w-2xl mx-auto animate-fade-in">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
            Your Preferences
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            Select the topics you care about. We'll personalize your news feed accordingly.
          </p>
        </div>

        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {Array.from({ length: 9 }).map((_, i) => (
              <div key={i} className="skeleton h-24 rounded-xl" />
            ))}
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-8">
              {CATEGORIES.map((cat) => {
                const isSelected = selected.includes(cat.id);
                return (
                  <button
                    key={cat.id}
                    onClick={() => toggleCategory(cat.id)}
                    className={`relative p-4 rounded-xl border-2 text-left transition-all duration-200 ${
                      isSelected
                        ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                        : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 hover:border-slate-300 dark:hover:border-slate-600"
                    }`}
                  >
                    {isSelected && (
                      <div className="absolute top-2 right-2 w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                        <FiCheck className="text-white text-xs" />
                      </div>
                    )}
                    <div className="text-2xl mb-2">{cat.emoji}</div>
                    <div className={`font-semibold text-sm ${isSelected ? "text-blue-700 dark:text-blue-400" : "text-slate-700 dark:text-slate-300"}`}>
                      {cat.label}
                    </div>
                  </button>
                );
              })}
            </div>

            <div className="flex items-center justify-between">
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {selected.length} categor{selected.length === 1 ? "y" : "ies"} selected
              </p>
              <div className="flex gap-3">
                <Link href="/" className="btn-secondary text-sm">
                  Cancel
                </Link>
                <button
                  onClick={handleSave}
                  disabled={saving || selected.length === 0}
                  className="btn-primary text-sm flex items-center gap-2"
                >
                  <FiSave />
                  {saving ? "Saving..." : "Save Preferences"}
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </ProtectedRoute>
  );
}
