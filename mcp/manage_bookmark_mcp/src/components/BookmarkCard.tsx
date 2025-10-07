"use client"

import type { Bookmark } from "@/types/bookmark"
import { Button } from "@/components/ui/button"
import { ExternalLink, Trash2, Calendar, Edit } from "lucide-react"
import { useState } from "react"

interface BookmarkCardProps {
  bookmark: Bookmark
  onDelete: (id: string) => void
  onEdit: (bookmark: Bookmark) => void
}

export default function BookmarkCard({ bookmark, onDelete, onEdit }: BookmarkCardProps) {
  const [isDeleting, setIsDeleting] = useState(false)

  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    })
  }

  const getDomain = (url: string) => {
    try {
      const domain = new URL(url).hostname
      return domain.replace("www.", "")
    } catch (error) {
      return "Invalid URL"
    }
  }

  const handleDelete = async () => {
    setIsDeleting(true)
    try {
      await onDelete(bookmark.id)
    } finally {
      setIsDeleting(false)
    }
  }

  const handleEdit = () => {
    onEdit(bookmark)
  }

  return (
    <div className="group relative bg-card border rounded-lg p-6 hover:bg-accent/50 transition-all duration-200 hover:shadow-lg">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-card-foreground text-lg mb-2 line-clamp-2 text-balance">
            {bookmark.title}
          </h3>
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-3">
            <span className="font-medium">{getDomain(bookmark.url)}</span>
            <span>•</span>
            <div className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              <span>{formatDate(bookmark.createdAt)}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0 hover:bg-primary/20 hover:text-primary"
            onClick={handleEdit}
          >
            <Edit className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0 hover:bg-destructive/20 hover:text-destructive"
            onClick={handleDelete}
            disabled={isDeleting}
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <a
        href={bookmark.url}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-2 text-sm text-primary hover:text-primary/80 transition-colors mb-4"
      >
        <span className="truncate max-w-[200px]">{bookmark.url}</span>
        <ExternalLink className="w-3 h-3 flex-shrink-0" />
      </a>

      {bookmark.notes && (
        <div className="mt-4 pt-4 border-t">
          <p className="text-sm text-muted-foreground line-clamp-3 text-pretty">{bookmark.notes}</p>
        </div>
      )}
    </div>
  )
}
