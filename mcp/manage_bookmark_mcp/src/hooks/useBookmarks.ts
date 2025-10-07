"use client";

import type { Bookmark, CreateBookmarkData } from "@/types/bookmark";
import { useEffect, useState } from "react";

export function useBookmarks() {
  const [bookmarks, setBookmarks] = useState<Bookmark[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBookmarks();
  }, []);

  const fetchBookmarks = async () => {
    try {
      setError(null);
      const response = await fetch("/api/bookmarks");

      if (!response.ok) {
        throw new Error("Failed to fetch bookmarks");
      }
      const data = await response.json();

      setBookmarks(data);
    } catch (error) {
      setError(error instanceof Error ? error.message : "An Error occurred");
    } finally {
      setLoading(false);
    }
  };

  const addBookmark = async (data: CreateBookmarkData) => {
    try {
      setError(null);
      const response = await fetch("/api/bookmarks", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error("Failed to add bookmark");
      }

      const newBookmark = await response.json();

      setBookmarks((prev) => [newBookmark, ...prev]);
      return newBookmark;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "An error occurred";
      setError(errorMessage);
    }
  };

  const updateBookmark = async (id: string, data: CreateBookmarkData) => {
    try {
      setError(null);
      const response = await fetch(`/api/bookmarks/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error("Failed to update bookmark");
      }

      const updatedBookmark: Bookmark = await response.json();

      setBookmarks((prev) =>
        prev.map((bookmark) =>
          bookmark.id === id ? updatedBookmark : bookmark
        )
      );
      return updatedBookmark;
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "An error occurred";
      setError(errorMessage);
    }
  };

  const deleteBookmark = async (id: string) => {
    try {
      setError(null);
      const response = await fetch(`/api/bookmarks/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete bookmark");
      }

      setBookmarks((prev) => prev.filter((bookmark) => bookmark.id !== id));
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "An error occurred";
      setError(errorMessage);
    }
  };

  return {
    bookmarks,
    loading,
    error,
    addBookmark,
    updateBookmark,
    deleteBookmark,
    refetch: fetchBookmarks,
  };
}
