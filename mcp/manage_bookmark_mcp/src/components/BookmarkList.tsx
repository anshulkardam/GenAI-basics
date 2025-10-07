"use client"

import type { Bookmark } from "@/types/bookmark"
import BookmarkCard from "./BookmarkCard"

interface BookmarkListProps {
  bookmarks: Bookmark[]
  onDelete: (id: string) => void
  onEdit: (bookmark: Bookmark) => void 
}

export default function BookmarkList({ bookmarks, onDelete, onEdit }: BookmarkListProps) {
  if (bookmarks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="w-16 h-16 mb-4 rounded-full bg-muted flex items-center justify-center">
          <svg className="w-8 h-8 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-foreground mb-2">No bookmarks yet</h3>
        <p className="text-muted-foreground max-w-sm">Start building your collection by adding your first bookmark</p>
      </div>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {bookmarks.map((bookmark) => (
        <BookmarkCard
          key={bookmark.id}
          bookmark={bookmark}
          onDelete={onDelete}
          onEdit={onEdit} 
        />
      ))}
    </div>
  )
}
